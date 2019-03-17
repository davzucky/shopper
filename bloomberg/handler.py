import boto3
import datetime
import requests
from botocore.exceptions import ClientError
from dataclasses import dataclass
from typing import Union


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
    price: str
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
    response = requests.get(
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker)
    )

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
            200,
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


def download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        s3.Bucket(bucket_name).download_file(file_key, tmp_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise


def append_ohlc_to_file(
    date: datetime.datetime, o: float, h: float, l: float, c: float, tmp_path: str
) -> None:
    with open(tmp_path, mode="a+") as f:
        f.write("{}\n".format(get_ohcl_row_str(date, o, h, l, c)))


def get_ohcl_row_str(
    date: datetime.datetime, o: float, h: float, l: float, c: float
) -> str:
    return "{:%Y-%M-%D},{:.6f},{:.6f},{:.6f},{:.6f}".format(date, o, h, l, c)


def upload_file_from_local_to_S3(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        s3.Bucket(bucket_name).upload_file(tmp_path, file_key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise


def handler(event, context):
    pass
