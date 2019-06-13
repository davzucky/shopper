import boto3
import botostubs
import pytest


@pytest.fixture(scope="function")
def clean_aws_sqs(terraform_output):
    sqs_queue_name = terraform_output["sqs_queue_name"]["value"]
    region = terraform_output["region"]["value"]
    sqs = boto3.resource("sqs", region_name=region)  # type: botostubs.SQS
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)
    queue.purge()
    yield


def test_lambda_function_check_setup(terraform_output):
    lambda_function_name = terraform_output["lambda_function_name"]["value"]
    region = terraform_output["region"]["value"]

    assert lambda_function_name == "tiingo_scheduler"

    client = boto3.client("lambda", region_name=region)
    lambda_configuration = client.get_function_configuration(
        FunctionName=lambda_function_name
    )
    assert lambda_configuration["Runtime"] == "python3.7"
    assert lambda_configuration["Timeout"] == 300
    assert "TIINGO_FETCHER_QUEUE" in lambda_configuration["Environment"]["Variables"]
    assert "TIINGO_TICKERS_FILE" in lambda_configuration["Environment"]["Variables"]
    assert "AWS_S3_BUCKET" in lambda_configuration["Environment"]["Variables"]


def test_deploy_1_event_rule(terraform_output):
    region = terraform_output["region"]["value"]
    events_client = boto3.client("events", region_name=region)  # type: botostubs.Events
    rules = events_client.list_rules()

    assert len(rules["Rules"]) == 1


@pytest.mark.parametrize(
    "event_rule, json_param",
    [("Monday_to_Friday_8pm_HKT", '[{"exchange": "SHE"}, {"exchange": "SHG"}]')],
)
def test_target_has_right_param_for_rule(
    terraform_output, event_rule: str, json_param: str
):
    lambda_function_arn = terraform_output["lambda_function_arn"]["value"]
    region = terraform_output["region"]["value"]
    events_client = boto3.client("events", region_name=region)  # type: botostubs.Events
    targets = events_client.list_targets_by_rule(Rule=event_rule)

    assert len(targets["Targets"]) == 1
    assert targets["Targets"][0]["Arn"] == lambda_function_arn
    assert targets["Targets"][0]["Input"] == json_param


@pytest.mark.parametrize(
    "json_filter,expect_nb_items",
    [('[{"exchange": "NASDAQ", "asset_type": "ETF"}]', 435)],
)
def test_lambda_trigger_is_sqs(
    clean_aws_sqs, terraform_output, json_filter: str, expect_nb_items: int
):
    sqs_queue_name = terraform_output["sqs_queue_name"]["value"]
    region = terraform_output["region"]["value"]
    lambda_function_arn = terraform_output["lambda_function_arn"]["value"]

    client_lambda = boto3.client("lambda", region_name=region)
    invoke_result = client_lambda.invoke(
        FunctionName=lambda_function_arn, InvocationType="Event", Payload=json_filter
    )

    assert invoke_result["StatusCode"] == 202

    sqs = boto3.resource("sqs", region_name=region)  # type: botostubs.SQS
    queue = sqs.get_queue_by_name(QueueName=sqs_queue_name)

    messages = set()

    for i in range(0, expect_nb_items):
        msg_list = queue.receive_messages(MaxNumberOfMessages=10)
        for msg in msg_list:
            messages.add(msg.body)
            msg.delete()

        if len(messages) == expect_nb_items:
            break

    assert len(messages) == expect_nb_items
