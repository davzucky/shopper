import json
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional, Iterable

import boto3
import daiquiri
from dataclass_csv import DataclassReader
from dataclasses_json import DataClassJsonMixin

from .aws_helpers import download_file_from_S3_to_temp
from .message import Message
from .os_helpers import get_env_variable_or_default, get_env_variable

daiquiri.setup(
    level=logging.getLevelName(
        get_env_variable_or_default("LAMBDA_LOGGING_LEVEL", "INFO")
    )
)

AWS_REGION = "AWS_REGION"
AWS_S3_BUCKET = "AWS_S3_BUCKET"
TIINGO_FETCHER_QUEUE = "TIINGO_FETCHER_QUEUE"
TIINGO_TICKERS_FILE = "TIINGO_TICKERS_FILE"


@dataclass
class TiingoTicker:
    ticker: str
    asset_type: str
    price_currency: str
    exchange: str = "Unknown"
    start_date: str = "1800-01-01"
    end_date: str = "2800-01-01"


def get_tiingo_tickers(tiingo_ticker_path: str) -> Iterable[TiingoTicker]:
    with open(tiingo_ticker_path) as tiingo_tickers_csv:
        tickers_datareader = DataclassReader(tiingo_tickers_csv, TiingoTicker)
        tickers_datareader.map("assetType").to("asset_type")
        tickers_datareader.map("priceCurrency").to("price_currency")
        tickers_datareader.map("startDate").to("start_date")
        tickers_datareader.map("endDate").to("end_date")
        for ticker in tickers_datareader:
            yield ticker


@dataclass()
class Filter(DataClassJsonMixin):
    exchange: Optional[str] = None
    asset_type: Optional[str] = None

    def filter_out(self, tiingo_ticker: TiingoTicker) -> bool:
        return (
            (self.asset_type is None) or (self.asset_type == tiingo_ticker.asset_type)
        ) and ((self.exchange is None) or (self.exchange == tiingo_ticker.exchange))


def handler(event: str, context):
    region = get_env_variable(AWS_REGION)
    bucket = get_env_variable(AWS_S3_BUCKET)
    sqs_queue_name = get_env_variable(TIINGO_FETCHER_QUEUE)
    tiingo_tickers = get_env_variable_or_default(
        TIINGO_TICKERS_FILE, "tiingo/tickers.csv"
    )

    tiingo_tickers_path = os.path.join(tempfile.gettempdir(), "tiingo_tickers.csv")
    download_file_from_S3_to_temp(region, bucket, tiingo_tickers, tiingo_tickers_path)

    tiingo_filters = Filter.schema().load(json.loads(event), many=True)
    sqs = boto3.resource("sqs", region_name=region)
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)

    for tiingo_filter in tiingo_filters:
        for tiingo_ticker in filter(
            tiingo_filter.filter_out, get_tiingo_tickers(tiingo_tickers_path)
        ):
            queue.send_message(
                MessageDeduplicationId=tiingo_ticker.ticker,
                MessageBody=Message(
                    tiingo_ticker.ticker,
                    f"market_data/{tiingo_ticker.ticker}/1d/data.csv",
                ).to_json(),
            )
