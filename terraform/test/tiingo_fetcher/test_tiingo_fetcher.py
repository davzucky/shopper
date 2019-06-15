import os
import time

import boto3
import botocore
import botostubs
import pytest

from tiingo_fetcher.aws_helpers import download_file_from_S3_to_temp
from .message import Message


@pytest.fixture(scope="function")
def clean_aws_resources(terraform_output):
    sqs_queue_name = terraform_output["sqs_queue_name"]["value"]
    region = terraform_output["region"]["value"]
    bucket_name = terraform_output["s3_bucket_name"]["value"]

    sqs = boto3.resource("sqs", region_name=region)  # type: botostubs.SQS
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    s3 = boto3.resource("s3", region_name=region)  # type: botostubs.S3
    bucket = s3.Bucket(bucket_name)

    bucket.objects.all().delete()
    yield
    queue.purge()
    bucket.objects.all().delete()


def test_output_contain_sqs_queue_name_init_with_tiingo_fetch(terraform_output):
    assert "tiingo_fetch-" in terraform_output["sqs_queue_name"]["value"]


def test_output_contain_s3_bucket_name_init_with_tiingo_fetch(terraform_output):
    assert "market-data-" in terraform_output["s3_bucket_name"]["value"]


def test_lambda_function_check_setup(terraform_output):
    lambda_function_name = terraform_output["lambda_function_name"]["value"]
    region = terraform_output["region"]["value"]

    client = boto3.client("lambda", region_name=region)
    lambda_configuration = client.get_function_configuration(
        FunctionName=lambda_function_name
    )
    assert lambda_configuration["Runtime"] == "python3.7"
    assert lambda_configuration["Timeout"] == 60
    assert "TIINGO_API_KEY" in lambda_configuration["Environment"]["Variables"]
    assert lambda_configuration["Environment"]["Variables"][
        "TIINGO_API_KEY"
    ] == os.environ.get("TIINGO_API_KEY")


def test_lambda_has_one_trigger_mapped_to(terraform_output):
    function_name = terraform_output["lambda_function_name"]["value"]
    region = terraform_output["region"]["value"]
    lambda_client = boto3.client("lambda", region_name=region)  # type: botostubs.Lambda
    lambda_tiingo = lambda_client.list_event_source_mappings(FunctionName=function_name)

    assert len(lambda_tiingo["EventSourceMappings"]) == 1


def test_lambda_deployement_values(terraform_output):
    function_name = terraform_output["lambda_function_name"]["value"]
    region = terraform_output["region"]["value"]
    lambda_client = boto3.client("lambda", region_name=region)  # type: botostubs.Lambda
    lambda_tiingo = lambda_client.list_event_source_mappings(FunctionName=function_name)

    assert (
        terraform_output["sqs_queue_arn"]["value"]
        == lambda_tiingo["EventSourceMappings"][0]["EventSourceArn"]
    )


def test_lambda_trigger_is_sqs(clean_aws_resources, terraform_output, tmpdir):
    sqs_queue_name = terraform_output["sqs_queue_name"]["value"]
    region = terraform_output["region"]["value"]
    bucket_name = terraform_output["s3_bucket_name"]["value"]

    ticker_name = "AAPL"
    bucker_file_key = "market_data/AAPL.US/1D/marketdata.csv"

    sqs = boto3.resource("sqs", region_name=region)  # type: botostubs.SQS
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    queue.send_message(MessageBody=Message(ticker_name, bucker_file_key).to_json())

    s3 = boto3.resource("s3", region_name=region)  # type: botostubs.S3

    max_try = 120
    for i in range(max_try + 1):
        try:
            s3.Object(bucket_name, bucker_file_key).load()
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "404":
                if i < max_try:
                    time.sleep(0.5)
                    continue
                else:
                    # The object does not exist.
                    AssertionError(
                        e.response["Error"],
                        "The file {} has not been saved to s3".format(bucker_file_key),
                    )
            else:
                # Something else has gone wrong.
                raise
        else:
            break

    local_path = os.path.join(tmpdir.dirname, "appl.csv")
    download_file_from_S3_to_temp(region, bucket_name, bucker_file_key, local_path)

    with open(local_path, "r") as f:
        lines = [l for l in f.readlines()]
        # 9683 is the number of row as of 9th of May 2019
        assert len(lines) >= 9683
