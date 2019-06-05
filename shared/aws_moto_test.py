import boto3
from contextlib import contextmanager

from moto import mock_s3, mock_sqs


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
