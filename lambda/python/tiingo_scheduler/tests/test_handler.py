import logging
import os
from typing import List, Dict

import boto3
import pytest
from moto import mock_lambda

from .aws_moto_test import setup_s3_bucket, setup_aws_lambda
from ..handler import (
    AWS_S3_BUCKET,
    AWS_REGION,
    TIINGO_TICKERS_FILE,
    handler,
    TIINGO_FETCHER_FUNCTION_NAME,
    LAMBDA_INVOCATION_TYPE,
)

LAMBDA_FUNCTION_CODE = """
def lambda_handler(event, context):
    records = event["records"]

    for e in records:
        print(e)
"""

LAMBDA_FUNCTION_CODE_ERROR = """
def lambda_handler(event, context):
    records = event["unknow_key"]

    for e in records:
        print(e)
"""


header = "ticker,exchange,assetType,priceCurrency,startDate,endDate"
message_1 = "000001,SHE,Stock,CNY,2007-08-30,2019-05-30\n000002,SHE,Stock,CNY,,"
message_2 = (
    "PZA,NYSE,ETF,USD,2007-10-18,2019-05-30\nPZA1,,Stock,USD,,\nPZAAX,"
    "NMFQS,Mutual Fund,USD,2011-11-02,2015-11-20 "
)


def get_function_string():
    current_path = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_path, "target_lambda_hander.py"), "r") as f:
        return f.read()


@pytest.mark.parametrize(
    "lambda_function_str,tiingo_tickers_csv_content,filter,tickers,nb_error,nb_info",
    [
        (LAMBDA_FUNCTION_CODE, header, [], [], 0, 2),
        (
            LAMBDA_FUNCTION_CODE,
            f"{header}\n{message_1}",
            [{}],
            ["000001", "000002"],
            0,
            1,
        ),
        (
            LAMBDA_FUNCTION_CODE,
            f"{header}\n{message_2}",
            [{"exchange": "NYSE", "asset_type": "ETF"}],
            ["PZA"],
            0,
            1,
        ),
        (
            LAMBDA_FUNCTION_CODE,
            f"{header}\n{message_2}\n{message_1}",
            [{}],
            ["000001", "000002", "PZA", "PZA1", "PZAAX"],
            0,
            1,
        ),
        (
            LAMBDA_FUNCTION_CODE,
            f"{header}\n{message_2}\n{message_1}",
            [{"asset_type": "Stock"}, {"asset_type": "ETF"}],
            ["000001", "000002", "PZA", "PZA1"],
            0,
            1,
        ),
    ],
)
@mock_lambda
def test_number_of_message_sent(
    monkeypatch,
    caplog,
    # tmpdir,
    lambda_function_str,
    tiingo_tickers_csv_content: str,
    filter: List[Dict[str, str]],
    tickers: List[str],
    nb_error,
    nb_info,
):
    region = "us-east-1"
    bucket_name = "market_data"
    function_name = "tiingo_fetcher"
    tiingo_file_path = "static/tiingo_tickers.csv"

    # Setup the required env variable
    monkeypatch.setenv(AWS_S3_BUCKET, bucket_name)
    monkeypatch.setenv(AWS_REGION, region)
    monkeypatch.setenv(TIINGO_FETCHER_FUNCTION_NAME, function_name)
    monkeypatch.setenv(TIINGO_TICKERS_FILE, tiingo_file_path)
    monkeypatch.setenv(LAMBDA_INVOCATION_TYPE, "RequestResponse")

    with setup_s3_bucket(region, bucket_name):
        with setup_aws_lambda(region, function_name, lambda_function_str):
            boto3.client("s3", region_name=region).put_object(
                Bucket=bucket_name,
                Key=tiingo_file_path,
                Body=tiingo_tickers_csv_content,
            )
            caplog.set_level(logging.ERROR)
            caplog.set_level(logging.INFO)
            handler(filter, None)

            assert nb_error == len(
                [
                    msg
                    for (fct, level, msg) in caplog.record_tuples
                    if level == logging.ERROR
                ]
            )
            assert nb_info == len(
                [
                    msg
                    for (fct, level, msg) in caplog.record_tuples
                    if level == logging.INFO
                ]
            )
