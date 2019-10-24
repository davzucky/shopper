import boto3
import daiquiri
from botocore.exceptions import ClientError

logger = daiquiri.getLogger(__name__)


def get_matching_s3_objects(bucket, prefix="", suffix=""):
    """
    Generate objects in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch objects whose key starts with
        this prefix (optional).
    :param suffix: Only fetch objects whose keys end with
        this suffix (optional).
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    kwargs = {"Bucket": bucket}

    # We can pass the prefix directly to the S3 API.  If the user has passed
    # a tuple or list of prefixes, we go through them one by one.
    if isinstance(prefix, str):
        prefixes = (prefix,)
    else:
        prefixes = prefix

    for key_prefix in prefixes:
        kwargs["Prefix"] = key_prefix

        for page in paginator.paginate(**kwargs):
            try:
                contents = page["Contents"]
            except KeyError:
                return

            for obj in contents:
                key = obj["Key"]
                if key.endswith(suffix):
                    yield obj


def get_matching_s3_keys(bucket, prefix="", suffix=""):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    for obj in get_matching_s3_objects(bucket, prefix, suffix):
        yield obj["Key"]


def download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.resource("s3", region_name=region_name)

    try:
        logger.debug(
            f"Download key {file_key} to {tmp_path} " f"from the bucket {bucket_name}"
        )

        s3.Bucket(bucket_name).download_file(file_key, tmp_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error(f"The object {file_key}  does not exist.")
        else:
            raise


def upload_file_from_local_to_S3(region_name, bucket_name, file_key, tmp_path) -> None:
    s3 = boto3.client("s3")

    try:
        s3.upload_file(file_key, bucket_name, tmp_path)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            logger.error(f"The object {file_key}  does not exist.")
        else:
            raise
