import sys
import os
import logging

from aws_xray_sdk.core.lambda_launcher import LambdaContext
from typing import Dict, Any

from .bloomberg import get_bloomberg_ticker_market_data, BloombergMarketDataError
from .messages import bloomberg as message

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_S3_BUCKET = "aws_s3_bucket"
AWS_REGION = "aws_region"


def get_bloomberg_message(record: Dict[str, Any]) -> message.BloombergMessage:
    return message.BloombergMessage.from_json(record["body"])


# @dispatch(BloombergMarketDataError)
# @overload
def process_market_data_error(data: BloombergMarketDataError):
    logger.warning("Error loading data from Bloomberg. {}".format(data.error))


# @dispatch(BloombergFundMarketData)
# # @overload
# def process_market_data(data: BloombergFundMarketData):
#     pass
# logger.warning("Error loading data from Bloomberg. {}".format(data.error))


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, "")
    if not variable:
        logger.error("The environement variable {} is not set.".format(env_var_name))
        sys.exit(-1)

    return variable


def handler(event: Dict[str, Any], context: LambdaContext):
    get_env_variable(AWS_S3_BUCKET)
    get_env_variable(AWS_REGION)

    for record in event["Records"]:
        message = get_bloomberg_message(record)
        market_data = get_bloomberg_ticker_market_data(message.ticker)
        if isinstance(market_data, BloombergMarketDataError):
            process_market_data_error(market_data)
