import requests
from typing import Union, Dict

import datetime

from dataclasses import dataclass

UNKNOWN_VALUE = "unknown"


@dataclass
class BloombergMarketData(object):
    pass


@dataclass
class BloombergMarketDataError(BloombergMarketData):
    status_code: int
    error: str


@dataclass
class MarketOHLC(object):
    date: datetime.date
    open: float
    high: float
    low: float
    close: float


@dataclass
class BloombergFundMarketData(BloombergMarketData, MarketOHLC):
    status_code: int
    id: str
    fundType: str
    fundObjective: str
    fundAssetClassFocus: str
    fundGeographicFocus: str
    totalReturn1Year: float
    totalReturnYtd: float
    name: str
    price: float
    issuedCurrency: str
    priceChange1Day: float
    percentChange1Day: float
    priceMinDecimals: int
    nyTradeStartTime: datetime.time
    nyTradeEndTime: datetime.time
    timeZoneOffset: int
    lastUpdateEpoch: int
    lowPrice52Week: float
    highPrice52Week: float


def get_date_from_epoch_offset(epoch: int, offset: int = 0) -> datetime.date:
    return (
        datetime.datetime.fromtimestamp(epoch) + datetime.timedelta(hours=offset)
    ).date()


def get_bloomberg_ticker_market_data(
    ticker: str
) -> Union[BloombergFundMarketData, BloombergMarketDataError]:
    headers = {
        "Host": "www.bloomberg.com",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:66.0) "
        "Gecko/20100101 Firefox/66.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    proxies: Dict[str, str] = {}
    response = requests.get(
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker),
        headers=headers,
        proxies=proxies,
    )

    print(response.content)

    if response.status_code == 200:
        json_response = response.json()
        return BloombergFundMarketData(
            get_date_from_epoch_offset(
                int(json_response.get("lastUpdateEpoch", "0")),
                json_response.get("timeZoneOffset", 0),
            ),
            json_response.get("price", 0),
            json_response.get("price", 0),
            json_response.get("price", 0),
            json_response.get("price", 0),
            response.status_code,
            json_response.get("id", UNKNOWN_VALUE),
            json_response.get("fundType", UNKNOWN_VALUE),
            json_response.get("fundObjective", UNKNOWN_VALUE),
            json_response.get("fundAssetClassFocus", UNKNOWN_VALUE),
            json_response.get("fundGeographicFocus", UNKNOWN_VALUE),
            json_response.get("totalReturn1year", 0.0),
            json_response.get("totalReturnYtd", 0.0),
            json_response.get("name", UNKNOWN_VALUE),
            json_response.get("price", 0),
            json_response.get("issuedCurrency", UNKNOWN_VALUE),
            json_response.get("priceChange1Day", 0.0),
            json_response.get("percentChange1Day", 0.0),
            json_response.get("priceMinDecimals", 2),
            datetime.time.fromisoformat(json_response.get("nyTradeStartTime", "0:0:0")),
            datetime.time.fromisoformat(
                json_response.get("nyTradeEndTime", "23:59:59")
            ),
            json_response.get("timeZoneOffset", 0),
            int(json_response.get("lastUpdateEpoch", "0")),
            json_response.get("lowPrice52Week", 0.0),
            json_response.get("highPrice52Week", 0.0),
        )

    return BloombergMarketDataError(response.status_code, response.text)
