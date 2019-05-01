import csv
import io
import logging
import os
import sys
from collections import OrderedDict
from typing import Dict, Any, Iterator, List

from tiingo import TiingoClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)

AWS_S3_BUCKET = "aws_s3_bucket"
AWS_REGION = "aws_region"

config = {}
config["session"] = True
client = TiingoClient(config)


def get_env_variable(env_var_name: str):
    variable = os.environ.get(env_var_name, "")
    if not variable:
        logger.error("The environement variable {} is not set.".format(env_var_name))
        sys.exit(-1)

    return variable


def handler(event: Dict[str, Any], context):
    # bucket = get_env_variable(AWS_S3_BUCKET)
    # region = get_env_variable(AWS_REGION)

    for record in event["Records"]:
        #     process_market_data(market_data, bucket, region, message.file_pa
        pass
        # message = get_bloomberg_message(record)
        # market_data = get_bloomberg_ticker_market_data(message.ticker)
        # if isinstance(market_data, BloombergMarketDataError):
        #     process_market_data_error(market_data)
        # elif isinstance(market_data, BloombergFundMarketData):


def get_tiingo_market_data(
    ticker: str,
    frequency: str = "daily",
    start_date: str = "1800-1-1",
    end_date: str = None,
) -> csv.DictReader:
    csv_prices = client.get_ticker_price(
        ticker, frequency=frequency, startDate=start_date, endDate=end_date, fmt="csv"
    )
    return csv.DictReader(io.StringIO(csv_prices))


def transform_to_output(input_data: Dict[str, object]) -> Dict[str, object]:
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


def get_csv_text(
    input_data: Iterator[Dict[str, object]],
    csv_columns: List[str] = ["date", "close", "high", "low", "open", "volume"],
) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=csv_columns, quoting=csv.QUOTE_NONE)
    writer.writeheader()
    writer.writerows(input_data)
    return output.getvalue()
