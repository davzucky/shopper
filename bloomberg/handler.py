import logging
import os
import sys
import tempfile
import uuid
from typing import Dict, Any

from bloomberg.aws import (
    download_file_from_S3_to_temp,
    append_ohlc_to_file,
    upload_file_from_local_to_S3,
)
from shared.message import get_messages_from_records
from .bloomberg import (
    get_bloomberg_ticker_market_data,
    BloombergMarketDataError,
    BloombergFundMarketData,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_S3_BUCKET = "aws_s3_bucket"
AWS_REGION = "aws_region"


def process_market_data_error(data: BloombergMarketDataError):
    logger.warning("Error loading data from Bloomberg. {}".format(data.error))


def process_market_data(
    data: BloombergFundMarketData, bucket_name: str, region_name: str, s3_file_key: str
):
    tmp_path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    download_file_from_S3_to_temp(region_name, bucket_name, s3_file_key, tmp_path)
    append_ohlc_to_file(
        data.date, data.price, data.price, data.price, data.price, tmp_path
    )
    upload_file_from_local_to_S3(region_name, bucket_name, s3_file_key, tmp_path)


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, "")
    if not variable:
        logger.error("The environement variable {} is not set.".format(env_var_name))
        sys.exit(-1)

    return variable


def handler(event: Dict[str, Any], context):
    bucket = get_env_variable(AWS_S3_BUCKET)
    region = get_env_variable(AWS_REGION)

    for message in get_messages_from_records(event):
        market_data = get_bloomberg_ticker_market_data(message.ticker)
        if isinstance(market_data, BloombergMarketDataError):
            process_market_data_error(market_data)
        elif isinstance(market_data, BloombergFundMarketData):
            process_market_data(market_data, bucket, region, message.file_path)
