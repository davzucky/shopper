import datetime

import boto3
import os
from contextlib import contextmanager
from moto import mock_s3

from bloomberg.aws import (
    download_file_from_S3_to_temp,
    append_ohlc_to_file,
    get_ohcl_row_str,
)

BUCKET = "some-bucket"
REGION_NAME = "us-east-1"
KEY = "bloomberg/myticker/1d/data.csv"
SAMPLE_CONTENT = "date,open,high,low,close\n2018-01-01,100,105,95,102\n"


def set_up_s3(bucket_name: str, region_name: str, file_key: str, file_content: str):
    conn = boto3.resource("s3", region_name=region_name)
    conn.create_bucket(Bucket=bucket_name)
    boto3.client("s3", region_name=region_name).put_object(
        Bucket=bucket_name, Key=file_key, Body=file_content
    )


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

        assert file_content == "{}{}".format(SAMPLE_CONTENT, new_row_str)


def test_if_date_already_exist_override_with_latest(tmpdir):
    file_name = "ticker.csv"
    file_path = os.path.join(tmpdir.dirname, file_name)
    with open(file_path, mode="w+") as f_ticker:
        f_ticker.write(SAMPLE_CONTENT)

    date = datetime.datetime(2018, 1, 2)
    open_price = 102.0
    high = 107.0
    low = 100.0
    close = 106.0

    append_ohlc_to_file(date, open_price, high, low, close, file_path)

    open_price = 102.0
    high = 109.0
    low = 100.0
    close = 107.0

    append_ohlc_to_file(date, open_price, high, low, close, file_path)

    file_content = open(file_path, "r").read()
    new_row_str = get_ohcl_row_str(date, open_price, high, low, close)

    assert file_content == "{}{}".format(SAMPLE_CONTENT, new_row_str)


def test_can_save_and_retrive_file_from_s3():
    with do_test_setup():
        conn = boto3.resource("s3", region_name=REGION_NAME)
        file_key = "bloomberg/myticker/1d/data.txt"
        obj = conn.Object(BUCKET, file_key)
        obj.put(Body=SAMPLE_CONTENT)

        obj_read = conn.Object(BUCKET, file_key).get()

        # Need to encode the string result because the stored value in S3 is encoded
        assert obj_read["Body"].read() == SAMPLE_CONTENT.encode()


@contextmanager
def do_test_setup(
    bucket_name: str = BUCKET,
    region_name: str = REGION_NAME,
    file_key: str = KEY,
    file_content: str = SAMPLE_CONTENT,
):
    with mock_s3():
        set_up_s3(bucket_name, region_name, file_key, file_content)
        yield
