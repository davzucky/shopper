import logging
import os
from typing import Dict, Any


logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_S3_BUCKET = "aws_s3_bucket"
AWS_REGION = "aws_region"


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, "")
    if not variable:
        logger.error("The environement variable {} is not set.".format(env_var_name))
        sys.exit(-1)

    return variable

def handler(event: Dict[str, Any], context):
    bucket = get_env_variable(AWS_S3_BUCKET)
    region = get_env_variable(AWS_REGION)

    for record in event["Records"]:
        message = get_bloomberg_message(record)
        market_data = get_bloomberg_ticker_market_data(message.ticker)
        if isinstance(market_data, BloombergMarketDataError):
            process_market_data_error(market_data)
        elif isinstance(market_data, BloombergFundMarketData):
            process_market_data(market_data, bucket, region, message.file_path)
