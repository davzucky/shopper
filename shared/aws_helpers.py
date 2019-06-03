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
