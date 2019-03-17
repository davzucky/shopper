import datetime

import boto3
from botocore.exceptions import ClientError


def download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        s3.Bucket(bucket_name).download_file(file_key, tmp_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise


def append_ohlc_to_file(
    date: datetime.datetime, o: float, h: float, l: float, c: float, tmp_path: str
) -> None:
    with open(tmp_path, mode="a+") as f:
        f.write("{}\n".format(get_ohcl_row_str(date, o, h, l, c)))


def get_ohcl_row_str(
    date: datetime.datetime, o: float, h: float, l: float, c: float
) -> str:
    return "{:%Y-%M-%D},{:.6f},{:.6f},{:.6f},{:.6f}".format(date, o, h, l, c)


def upload_file_from_local_to_S3(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        s3.Bucket(bucket_name).upload_file(tmp_path, file_key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise
