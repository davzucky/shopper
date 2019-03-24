import itertools

import boto3
import datetime
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
    date: datetime.date, o: float, h: float, l: float, c: float, tmp_path: str
) -> None:

    with open(tmp_path, mode="r") as f_read:
        lines = f_read.readlines()

    formatted_date = get_date_formatted(date)
    with open(tmp_path, mode="w+") as f_write:
        f_write.writelines(
            itertools.filterfalse(lambda l: l.startswith(formatted_date), lines)
        )
        f_write.write(get_ohcl_row_str(date, o, h, l, c))


def get_date_formatted(date: datetime.date) -> str:
    return "{:%Y-%m-%d}".format(date)


def get_ohcl_row_str(
    date: datetime.date, o: float, h: float, l: float, c: float
) -> str:
    return "{},{:.6f},{:.6f},{:.6f},{:.6f}".format(get_date_formatted(date), o, h, l, c)


def upload_file_from_local_to_S3(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        s3.Bucket(bucket_name).upload_file(tmp_path, file_key)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        else:
            raise
