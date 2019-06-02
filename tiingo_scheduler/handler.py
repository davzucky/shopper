from dataclasses import dataclass
from typing import Dict, Any

from dataclass_csv import DataclassReader


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


def handler(event: Dict[str, Any], context):
    pass
