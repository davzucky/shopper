import csv
import io
import logging
import tempfile
from collections import OrderedDict
from typing import Dict, Any, Iterator, List

import daiquiri
from tiingo import TiingoClient

from .aws_helpers import upload_file_from_local_to_S3
from .message import get_messages_from_records
from .os_helpers import get_env_variable, get_env_variable_or_default

AWS_S3_BUCKET = "AWS_S3_BUCKET"
AWS_REGION = "AWS_REGION"

config = {}
config["session"] = True
client = TiingoClient(config)


daiquiri.setup(
    level=logging.getLevelName(
        get_env_variable_or_default("LAMBDA_LOGGING_LEVEL", "INFO")
    )
)


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
    csv_columns: List[str] = ["date", "close", "high", "low", "open", "volume"],
):
    with open(file_path, "w") as output:
        writer = csv.DictWriter(output, fieldnames=csv_columns, quoting=csv.QUOTE_NONE)
        writer.writeheader()
        writer.writerows(input_data)


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
        upload_file_from_local_to_S3(region, bucket, tmp_file, message.file_path)
