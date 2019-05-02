import csv
import io
import logging
import os
import sys
import tempfile
from collections import OrderedDict
from typing import Dict, Any, Iterator, List

import boto3
from botocore.exceptions import ClientError
from tiingo import TiingoClient

from .message import get_messages_from_records

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_S3_BUCKET = "aws_s3_bucket"
AWS_REGION = "aws_region"

config = {}
config["session"] = True
client = TiingoClient(config)


def get_tiingo_market_data(
    ticker: str,
    frequency: str = "daily",
    start_date: str = "1800-1-1",
    end_date: str = None,
    # ) -> Iterator[typing.OrderedDict[str, object]]:
) -> csv.DictReader:
    csv_prices = client.get_ticker_price(
        ticker, frequency=frequency, startDate=start_date, endDate=end_date, fmt="csv"
    )
    return csv.DictReader(io.StringIO(csv_prices))


def transform_to_output(input_data: OrderedDict) -> Dict[str, object]:
    return OrderedDict(
        [
            ("date", input_data["date"]),
            ("close", input_data["adjClose"]),
            ("high", input_data["adjHigh"]),
            ("low", input_data["adjLow"]),
            ("open", input_data["adjOpen"]),
            ("volume", input_data["adjVolume"]),
        ]
    )


def save_to_csv_file(
    input_data: Iterator[Dict[str, object]],
    file_path: str,
    csv_columns: List[str] = ["date", "close", "high", "low", "open", "volume"]
):
    with open(file_path, "w") as output:
        writer = csv.DictWriter(output, fieldnames=csv_columns, quoting=csv.QUOTE_NONE)
        writer.writeheader()
        writer.writerows(input_data)


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, "")
    if not variable:
        logger.error("The environement variable {} is not set.".format(env_var_name))
        sys.exit(-1)

    return variable


def upload_file_from_local_to_S3(region_name, bucket_name, file_key, tmp_path) -> None:
    # s3 = boto3.resource("s3", region_name=region_name)
    s3 = boto3.client('s3', region_name=region_name)
    try:
        s3.upload_file(file_key, bucket_name, tmp_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise


def handler(event: Dict[str, Any], context):
    bucket = get_env_variable(AWS_S3_BUCKET)
    region = get_env_variable(AWS_REGION)

    for message in get_messages_from_records(event):
        market_data = get_tiingo_market_data(message.ticker, "daily")
        tmp_file = tempfile.NamedTemporaryFile().name
        print("save temp result to {}".format(tmp_file))
        save_to_csv_file(map(transform_to_output, market_data), tmp_file)
        with open(tmp_file, "r") as result_file:
            nb_lines = len(result_file.readlines())
            print("The file {} contain {} lines".format(tmp_file, nb_lines))
        # print("save temp result to {}".format(tmp_file))
        upload_file_from_local_to_S3(region, bucket, tmp_file, message.file_path)

        #     process_market_data(market_data, bucket, region, message.file_pa
        # pass
        # message = get_bloomberg_message(record)
        # market_data = get_bloomberg_ticker_market_data(message.ticker)
        # if isinstance(market_data, BloombergMarketDataError):
        #     process_market_data_error(market_data)
        # elif isinstance(market_data, BloombergFundMarketData):
