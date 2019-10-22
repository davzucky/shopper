import json
import os
import sys

import boto3
import botostubs
import pytest

from .aws_helpers import download_file_from_S3_to_temp
from .share import (
    lambda_function_check_setup,
    lambda_function_setup_contain_env_var,
    lambda_function_check_env_var_value,
)
from .message import Message


@pytest.fixture()
def s3_base_path():
    return "market_data_tiingo_fetcher/"


@pytest.fixture(scope="function")
def clean_aws_resources(terraform_output, s3_base_path, s3_bucket_name):
    region = terraform_output["region"]["value"]

    s3 = boto3.resource("s3", region_name=region)  # type: botostubs.S3
    bucket = s3.Bucket(s3_bucket_name)

    for key in bucket.objects.filter(Prefix=s3_base_path):
        key.delete()
    yield
    for key in bucket.objects.filter(Prefix=s3_base_path):
        key.delete()


def test_tiingo_fetcher_lambda_setup(terraform_output):
    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]
    expected_timeout = 300

    lambda_function_check_setup(lambda_function_name, region, expected_timeout)


@pytest.mark.parametrize("env_var", [("TIINGO_API_KEY"), ("AWS_S3_BUCKET")])
def test_tiingo_fetcher_contain_env_var(terraform_output, env_var: str):

    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]

    lambda_function_setup_contain_env_var(lambda_function_name, region, env_var)


@pytest.mark.parametrize(
    "env_var, value", [("TIINGO_API_KEY", os.environ.get("TIINGO_API_KEY"))]
)
def test_tiingo_fetcher_env_var_has_right_value(
    terraform_output, env_var: str, value: str
):
    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]

    lambda_function_check_env_var_value(lambda_function_name, region, env_var, value)


def test_tiingo_fetcher_s3_bucket_is_set_with_right_value(
    terraform_output, s3_bucket_name
):
    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]
    env_var = "AWS_S3_BUCKET"

    lambda_function_check_env_var_value(
        lambda_function_name, region, env_var, s3_bucket_name
    )


def test_lambda_download_files_from_tiingo(
    clean_aws_resources, terraform_output, tmpdir, s3_base_path
):
    tiingo_fetcher_fnct_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]
    bucket_name = terraform_output["s3_bucket_name"]["value"]

    tickers = [{"ticker": "AAPL", "nbRows": 9683}, {"ticker": "MSFT", "nbRows": 8460}]
    messages = [
        json.loads(
            Message(
                ticker["ticker"], f"{s3_base_path}{ticker['ticker']}/1D/marketdata.csv"
            ).to_json()
        )
        for ticker in tickers
    ]
    request = {"records": messages}
    payload = json.dumps(request)

    lambda_client = boto3.client("lambda", region_name=region)

    lambda_call_result = lambda_client.invoke(
        FunctionName=tiingo_fetcher_fnct_name,
        InvocationType="RequestResponse",
        Payload=payload,
    )

    assert 200 == lambda_call_result["StatusCode"]
    assert "Handled" == lambda_call_result.get("FunctionError", "Handled")

    def get_num_rows(ticker: str) -> int:
        for tick_info in [t for t in tickers if t["ticker"] == ticker]:
            return tick_info["nbRows"]
        return sys.maxsize

    for message in messages:
        local_path = os.path.join(tmpdir.dirname, f"{message['ticker']}.csv")
        download_file_from_S3_to_temp(
            region, bucket_name, message["file_path"], local_path
        )

        with open(local_path, "r") as f:
            lines = [l for l in f.readlines()]
            # 9683 is the number of row as of 9th of May 2019
            assert len(lines) >= get_num_rows(message["ticker"])
