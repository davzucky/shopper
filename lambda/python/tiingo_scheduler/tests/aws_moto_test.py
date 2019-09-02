import io
import zipfile
from typing import Dict

import boto3
from contextlib import contextmanager

from moto import mock_s3, mock_sqs, mock_lambda

_lambda_region = "us-east-1"
boto3.setup_default_session(region_name=_lambda_region)


def _process_lambda(func_str):
    zip_output = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED)
    zip_file.writestr("lambda_function.py", func_str)
    zip_file.close()
    zip_output.seek(0)
    return zip_output.read()


@contextmanager
def setup_aws_lambda(
    region_name: str, func_name: str, func_str: str, environment: Dict[str, str] = {}
):
    with mock_lambda():
        lambda_client = boto3.client("lambda", region_name)
        lambda_client.create_function(
            FunctionName=func_name,
            Runtime="python3.6",
            Role="test-iam-role",
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": _process_lambda(func_str)},
            Environment={"Variables": environment},
            Description="test lambda function",
            Timeout=3,
            MemorySize=128,
            Publish=True,
        )
        yield


@contextmanager
def setup_s3_bucket(region_name: str, bucket_name: str):
    with mock_s3():
        s3 = boto3.resource("s3", region_name=region_name)
        s3.create_bucket(Bucket=bucket_name)
        yield


@contextmanager
def setup_sqs(region_name: str, queue_name: str):
    with mock_sqs():
        sqs = boto3.resource("sqs", region_name=region_name)
        queue = sqs.create_queue(QueueName=queue_name)
        yield queue
