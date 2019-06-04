import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

import daiquiri
from dataclass_csv import DataclassReader
from dataclasses_json import DataClassJsonMixin

from .os_helpers import get_env_variable_or_default

daiquiri.setup(
    level=logging.getLevelName(
        get_env_variable_or_default("LAMBDA_LOGGING_LEVEL", "INFO")
    )
)

AWS_REGION = "AWS_REGION"
AWS_S3_BUCKET = "AWS_S3_BUCKET"
TIINGO_TICKERS_FILE = "TIINGO_TICKERS_FILE"


def get_tiingo_tickers(tiingo_ticker_path: str):
    with open(tiingo_ticker_path) as tiingo_tickers_csv:
        tickers_datareader = DataclassReader(tiingo_tickers_csv, TiingoTicker)
        tickers_datareader.map("assetType").to("asset_type")
        tickers_datareader.map("priceCurrency").to("price_currency")
        tickers_datareader.map("startDate").to("start_date")
        tickers_datareader.map("endDate").to("end_date")
        for ticker in tickers_datareader:
            yield ticker


@dataclass
class TiingoTicker:
    ticker: str
    asset_type: str
    price_currency: str
    exchange: str = "Unknown"
    start_date: str = "1800-01-01"
    end_date: str = "2800-01-01"


@dataclass()
class Filter(DataClassJsonMixin):
    exchange: Optional[str] = None
    asset_type: Optional[str] = None

    def filter_out(self, tiingo_ticker: TiingoTicker) -> bool:
        return (
            (self.asset_type is None) or (self.asset_type == tiingo_ticker.asset_type)
        ) and ((self.exchange is None) or (self.exchange == tiingo_ticker.exchange))


def handler(event: Dict[str, Any], context):
    pass
