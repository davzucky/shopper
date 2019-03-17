import boto3
import datetime
import os
from contextlib import contextmanager
from moto import mock_s3

from ..handler import (
    download_file_from_S3_to_temp,
    append_ohlc_to_file,
    get_ohcl_row_str,
    get_bloomberg_ticker_market_data,
    BloombergFundMarketData,
    BloombergMarketDataError,
)

BUCKET = "some-bucket"
REGION_NAME = "us-east-1"
KEY = "bloomberg/myticker/1d/data.csv"
SAMPLE_CONTENT = "date,open,high,low,close\n2018-01-01,100,105,95,102\n"

UNKNOWN_SAMPLE_DATA = {"securityType": "UNKNOWN"}


FUND_SAMPLE_DATA = {
    "id": "JPMPCAA:HK",
    "fundType": "Open-End Fund",
    "fundObjective": "Conservative Allocation",
    "fundAssetClassFocus": "Mixed Allocation",
    "fundGeographicFocus": "North American Region",
    "totalReturn1Year": -2.594618,
    "totalReturnYtd": 4.767293,
    "name": "JPMorgan Provident Capital Fund",
    "price": 240.64,
    "issuedCurrency": "HKD",
    "priceChange1Day": 0.14,
    "percentChange1Day": 0.05821206,
    "priceMinDecimals": 2,
    "nyTradeStartTime": "01:00:00.000",
    "nyTradeEndTime": "23:59:00.000",
    "timeZoneOffset": -4,
    "lastUpdateEpoch": "1552453170",
    "lowPrice52Week": 229.09,
    "highPrice52Week": 247.27,
}


@contextmanager
def do_test_setup():
    with mock_s3():
        set_up_s3()
        yield


def set_up_s3():
    bucket_name = BUCKET
    region_name = REGION_NAME
    file_key = KEY
    body = SAMPLE_CONTENT

    conn = boto3.resource("s3", region_name=region_name)
    conn.create_bucket(Bucket=bucket_name)
    boto3.client("s3", region_name=region_name).put_object(
        Bucket=bucket_name, Key=file_key, Body=body
    )


def test_when_ticker_valid_ticker_return_fund_object(requests_mock):
    ticker = "JPMPCAA:HK"
    requests_mock.register_uri(
        "GET",
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker),
        json=FUND_SAMPLE_DATA,
        status_code=200,
    )
    return_value = get_bloomberg_ticker_market_data(ticker)
    assert type(return_value) == BloombergFundMarketData
    assert return_value.status_code == 200
    assert return_value.price == 240.64
    assert return_value.open == 240.64
    assert return_value.high == 240.64
    assert return_value.low == 240.64
    assert return_value.close == 240.64
    assert return_value.date == datetime.datetime(2019, 3, 13).date()


def test_when_ticker_not_valid_return_unknow(requests_mock):
    ticker = "UNKNOW"
    requests_mock.register_uri(
        "GET",
        "https://www.bloomberg.com/markets/api/security/basic/{}".format(ticker),
        json=UNKNOWN_SAMPLE_DATA,
        status_code=304,
    )

    return_value = get_bloomberg_ticker_market_data(ticker)

    assert type(return_value) == BloombergMarketDataError
    assert return_value.status_code == 304

    assert return_value.error == '{"securityType": "UNKNOWN"}'


def test_can_download_file_from_S3_to_temp_and_have_same_content(tmpdir):
    with do_test_setup():
        # Setup the file in S3
        tmp_path = os.path.join(tmpdir.dirname, "ticker_tmp.csv")
        bucket_name = BUCKET
        region_name = REGION_NAME
        file_key = KEY

        download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path)

        file_content = open(tmp_path, "r").read()
        assert file_content == SAMPLE_CONTENT


def test_add_ohlc_data_to_file(tmpdir):
    with do_test_setup():
        # Setup the file in S3
        bucket_name = BUCKET
        region_name = REGION_NAME
        file_key = "bloomberg/myticker/1d/data.csv"
        tmp_path = os.path.join(tmpdir.dirname, "ticker_tmp.csv")

        download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path)

        date = datetime.datetime(2018, 1, 2)
        open_price = 102.0
        high = 107.0
        low = 100.0
        close = 106.0
        append_ohlc_to_file(date, open_price, high, low, close, tmp_path)

        file_content = open(tmp_path, "r").read()
        new_row_str = get_ohcl_row_str(date, open_price, high, low, close)

        assert file_content == "{}{}\n".format(SAMPLE_CONTENT, new_row_str)


def test_can_save_and_retrive_file_from_s3():
    with do_test_setup():
        conn = boto3.resource("s3", region_name=REGION_NAME)
        file_key = "bloomberg/myticker/1d/data.txt"
        obj = conn.Object(BUCKET, file_key)
        obj.put(Body=SAMPLE_CONTENT)

        obj_read = conn.Object(BUCKET, file_key).get()

        # Need to encode the string result because the stored value in S3 is encoded
        assert obj_read["Body"].read() == SAMPLE_CONTENT.encode()


def get_sample_sqs_message(ticker: str, s3_bucket: str, file_key: str):
    return {
        "Records": [
            {
                "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                "receiptHandle": "EMPTY",
                "body": '{"foo":"bar"}',
                "attributes": {
                    "ApproximateReceiveCount": "3",
                    "SentTimestamp": "1529104986221",
                    "SenderId": "594035263019",
                    "ApproximateFirstReceiveTimestamp": "1529104986230",
                },
                "messageAttributes": {},
                "md5OfBody": "9bb58f26192e4ba00f01e2e7b136bbd8",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-west-2:594035263019:NOTFIFOQUEUE",
                "awsRegion": "us-west-2",
            }
        ]
    }
