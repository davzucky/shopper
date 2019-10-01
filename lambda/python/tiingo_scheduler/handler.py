import base64
import json
import logging
import os
import tempfile
from dataclasses import dataclass
from typing import Optional, Iterable, Dict, Any

import boto3
import daiquiri
from dataclass_csv import DataclassReader
from dataclasses_json import DataClassJsonMixin
from more_itertools import grouper

from .aws_helpers import download_file_from_S3_to_temp
from .message import Message
from .os_helpers import get_env_variable_or_default, get_env_variable

daiquiri.setup(
    level=logging.getLevelName(
        get_env_variable_or_default("LAMBDA_LOGGING_LEVEL", "INFO")
    )
)

logger = daiquiri.getLogger(__name__)

AWS_REGION = "AWS_REGION"
AWS_S3_BUCKET = "AWS_S3_BUCKET"
TIINGO_FETCHER_FUNCTION_NAME = "TIINGO_FETCHER_FUNCTION_NAME"
TIINGO_TICKERS_FILE = "TIINGO_TICKERS_FILE"
LAMBDA_INVOCATION_TYPE = "LAMBDA_INVOCATION_TYPE"


@dataclass(eq=True, frozen=True)
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


def handler(message: Dict[str, Any], context):
    region = get_env_variable(AWS_REGION)
    bucket = get_env_variable(AWS_S3_BUCKET)
    target_function_name = get_env_variable(TIINGO_FETCHER_FUNCTION_NAME)
    tiingo_tickers = get_env_variable_or_default(
        TIINGO_TICKERS_FILE, "tiingo/tickers.csv"
    )
    invocation_type = get_env_variable_or_default(LAMBDA_INVOCATION_TYPE, "Event")
    filters = message["filters"]
    base_path = message.get("base_path", "market_data")
    tiingo_filters = Filter.schema().load(filters, many=True)
    logger.debug(f"Number of filters : {len(tiingo_filters)}")

    tiingo_tickers_path = os.path.join(tempfile.gettempdir(), "tiingo_tickers.csv")
    download_file_from_S3_to_temp(region, bucket, tiingo_tickers, tiingo_tickers_path)

    lambda_client = boto3.client("lambda", region_name=region)

    nb_msg_send = 0
    for tiingo_filter in tiingo_filters:
        logger.debug(f"run filter: {tiingo_filter}")
        tickers = set(
            filter(tiingo_filter.filter_out, get_tiingo_tickers(tiingo_tickers_path))
        )
        for tiingo_tickers in grouper(10, tickers):
            nb_msg_send += len(tiingo_tickers)
            messages = [
                Message(
                    tiingo_ticker.ticker,
                    f"{base_path}/{tiingo_ticker.ticker}/1d/data.csv",
                )
                for tiingo_ticker in tiingo_tickers
                if tiingo_ticker is not None
            ]
            event = {"records": Message.schema().dump(messages, many=True)}
            payload = json.dumps(event)
            logger.debug(f"send -> {payload}")

            lambda_call_result = lambda_client.invoke(
                FunctionName=target_function_name,
                InvocationType=invocation_type,
                Payload=payload,
            )

            if lambda_call_result["StatusCode"] in (200, 202, 204) and (
                "FunctionError" not in lambda_call_result.keys()
            ):
                continue
            error_msg = f"Call to {target_function_name} Error. \
                {lambda_call_result['FunctionError']}-\
                {base64.b64decode(lambda_call_result['LogResult']).decode('utf-8')}"

            logger.error(error_msg)
            raise Exception(error_msg)
    logger.info(f"Numbers of messages sent: {nb_msg_send}")
