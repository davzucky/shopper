from typing import List

import boto3
import pytest

from ..message import Message
from ..handler import (
    AWS_S3_BUCKET,
    AWS_REGION,
    TIINGO_FETCHER_QUEUE,
    TIINGO_TICKERS_FILE,
    handler,
)
from .aws_moto_test import setup_s3_bucket, setup_sqs


# def add_content_to_s3(region, bucket, key, content):

header = "ticker,exchange,assetType,priceCurrency,startDate,endDate"
message_1 = "000001,SHE,Stock,CNY,2007-08-30,2019-05-30\n000002,SHE,Stock,CNY,,"
message_2 = (
    "PZA,NYSE,ETF,USD,2007-10-18,2019-05-30\nPZA1,,Stock,USD,,\nPZAAX,"
    "NMFQS,Mutual Fund,USD,2011-11-02,2015-11-20 "
)


@pytest.mark.parametrize(
    "tiingo_tickers_csv_content,filter,tickers",
    [
        (header, "[]", []),
        (f"{header}\n{message_1}", "[{}]", ["000001", "000002"]),
        (
            f"{header}\n{message_2}",
            '[{"exchange": "NYSE", "asset_type": "ETF"}]',
            ["PZA"],
        ),
        (
            f"{header}\n{message_2}\n{message_1}",
            "[{}]",
            ["000001", "000002", "PZA", "PZA1", "PZAAX"],
        ),
        (
            f"{header}\n{message_2}\n{message_1}",
            '[{"asset_type": "Stock"}, {"asset_type": "ETF"}]',
            ["000001", "000002", "PZA", "PZA1"],
        ),
    ],
)
def test_number_of_message_sent(
    monkeypatch, tiingo_tickers_csv_content: str, filter: str, tickers: List[str]
):
    region = "us-east-1"
    bucket_name = "market_data"
    queue_name = "tiingo_fetcher"
    tiingo_file_path = "static/tiingo_tickers.csv"

    # Setup the required env variable
    monkeypatch.setenv(AWS_S3_BUCKET, bucket_name)
    monkeypatch.setenv(AWS_REGION, region)
    monkeypatch.setenv(TIINGO_FETCHER_QUEUE, queue_name)
    monkeypatch.setenv(TIINGO_TICKERS_FILE, tiingo_file_path)

    with setup_s3_bucket(region, bucket_name):
        with setup_sqs(region, queue_name) as queue:
            boto3.client("s3", region_name=region).put_object(
                Bucket=bucket_name,
                Key=tiingo_file_path,
                Body=tiingo_tickers_csv_content,
            )
            handler(filter, None)

            messages = set()

            for i in range(0, len(tickers)):
                msg_list = queue.receive_messages(
                    VisibilityTimeout=1, MaxNumberOfMessages=10, WaitTimeSeconds=5
                )
                for msg in msg_list:
                    messages.add(msg.body)
                    msg.delete()

            result_messages = set(
                [
                    Message(ticker, f"market_data/{ticker}/1d/data.csv").to_json()
                    for ticker in tickers
                ]
            )

            assert len(messages) == len(tickers)
            assert messages == result_messages
