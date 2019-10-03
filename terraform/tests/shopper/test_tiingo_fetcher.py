import json
import os

import boto3
import botostubs
import pytest

from terraform.tests.shopper.share import lambda_function_check_setup, \
    lambda_function_setup_contain_env_var, lambda_function_check_env_var_value
from .message import Message


@pytest.fixture()
def s3_base_path():
    return "market_data_tiingo_fetcher/"


@pytest.fixture(scope="function")
def clean_aws_resources(terraform_output, s3_base_path, s3_bucket_name):
    region = terraform_output["region"]["value"]
    # bucket_name = terraform_output["s3_bucket_name"]["value"]

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
    expected_timeout = 60

    lambda_function_check_setup(lambda_function_name, region, expected_timeout)


@pytest.mark.parametrize("env_var", [
    ("TIINGO_API_KEY"),
    ("AWS_S3_BUCKET"),
    ("AWS_REGION"),
])
def test_tiingo_fetcher_contain_env_var(terraform_output, env_var: str):

    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]

    lambda_function_setup_contain_env_var(lambda_function_name, region, env_var)

@pytest.mark.parametrize("env_var, value", [
    ("TIINGO_API_KEY", os.environ.get("TIINGO_API_KEY")),
])
def test_tiingo_fetcher_contain_env_var(terraform_output, env_var: str, value: str):
    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]

    lambda_function_check_env_var_value(lambda_function_name, region, env_var, value)

def test_tiingo_fetcher_s3_bucket_is_set_with_right_value(terraform_output, s3_bucket_name):
    lambda_function_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]
    env_var = "AWS_S3_BUCKET"

    lambda_function_check_env_var_value(lambda_function_name, region, env_var, s3_bucket_name)



# def test_lambda_has_one_trigger_mapped_to(terraform_output):
#     function_name = terraform_output["lambda_function_name"]["value"]
#     region = terraform_output["region"]["value"]
#     lambda_client = boto3.client("lambda", region_name=region)  # type: botostubs.Lambda
#     lambda_tiingo = lambda_client.list_event_source_mappings(FunctionName=function_name)
#
#     assert len(lambda_tiingo["EventSourceMappings"]) == 1
#
#
# def test_lambda_deployement_values(terraform_output):
#     function_name = terraform_output["lambda_function_name"]["value"]
#     region = terraform_output["region"]["value"]
#     lambda_client = boto3.client("lambda", region_name=region)  # type: botostubs.Lambda
#     lambda_tiingo = lambda_client.list_event_source_mappings(FunctionName=function_name)
#
#     assert (
#         terraform_output["sqs_queue_arn"]["value"]
#         == lambda_tiingo["EventSourceMappings"][0]["EventSourceArn"]
#     )
#
#

def test_lambda_trigger_is_sqs(clean_aws_resources, terraform_output, tmpdir, s3_base_path):
    tiingo_fetcher_fnct_name = terraform_output["tiingo_fetcher_name"]["value"]
    region = terraform_output["region"]["value"]
    bucket_name = terraform_output["s3_bucket_name"]["value"]

    tickers = ["AAPL", "MSFT"]
    messages = [json.loads(Message(ticker, f"{s3_base_path}/{ticker}/1D/marketdata.csv").to_json()) for ticker in tickers]
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


    #
    # s3 = boto3.resource("s3", region_name=region)  # type: botostubs.S3
    #
    # max_try = 120
    # for i in range(max_try + 1):
    #     try:
    #         s3.Object(bucket_name, bucker_file_key).load()
    #     except botocore.exceptions.ClientError as e:
    #         if e.response["Error"]["Code"] == "404":
    #             if i < max_try:
    #                 time.sleep(0.5)
    #                 continue
    #             else:
    #                 # The object does not exist.
    #                 AssertionError(
    #                     e.response["Error"],
    #                     "The file {} has not been saved to s3".format(bucker_file_key),
    #                 )
    #         else:
    #             # Something else has gone wrong.
    #             raise
    #     else:
    #         break
    #
    # local_path = os.path.join(tmpdir.dirname, "appl.csv")
    # download_file_from_S3_to_temp(region, bucket_name, bucker_file_key, local_path)
    #
    # with open(local_path, "r") as f:
    #     lines = [l for l in f.readlines()]
    #     # 9683 is the number of row as of 9th of May 2019
    #     assert len(lines) >= 9683
