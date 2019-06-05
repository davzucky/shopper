from .aws_moto_test import setup_s3_bucket, setup_sqs


# def add_content_to_s3(region, bucket, key, content):


def test_the_root_handler():
    region = "us-east-1"
    bucket_name = "market_data"
    queue_name = "tiingo_fetcher"

    with setup_s3_bucket(region, bucket_name):
        with setup_sqs(region, queue_name):
            pass
