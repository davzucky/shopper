import boto3
import botostubs

def test_output_contain_sqs_queue_name_init_with_tiingo_fetch(terraform_output):
    assert "tiingo_fetch-" in terraform_output["sqs_queue_name"]["value"]


def test_output_contain_s3_bucket_name_init_with_tiingo_fetch(terraform_output):
    assert "market-data-" in terraform_output["s3_bucket_name"]["value"]


def test_lambda_trigger_is_sqs(terraform_output):
    function_name = terraform_output["lambda_function_name"]["value"]
    region = terraform_output["region"]["value"]
    lambda_client = boto3.client('lambda', region_name=region) # type: botostubs.Lambda
    lambda_tiingo = lambda_client.list_event_source_mappings(FunctionName=function_name)

    assert terraform_output["sqs_queue_name"]["value"] in lambda_tiingo["EventSourceMappings"][0]["EventSourceArn"]