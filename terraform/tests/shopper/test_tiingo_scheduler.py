import json
from datetime import datetime
from typing import List

import boto3
import botostubs
import pytest

from .aws_helpers import get_matching_s3_keys
from .share import lambda_function_check_setup, lambda_function_setup_contain_env_var


def test_tiingo_scheduler_lambda_python_setup(version, environment, terraform_output):
    lambda_function_name = terraform_output["tiingo_scheduler_name"]["value"]
    region = terraform_output["region"]["value"]
    expected_timeout = 300
    lambda_function_check_setup(lambda_function_name, region, expected_timeout)


@pytest.mark.parametrize(
    "env_var",
    [
        ("AWS_S3_BUCKET"),
        ("TIINGO_FETCHER_FUNCTION_NAME"),
        ("LAMBDA_INVOCATION_TYPE"),
        ("TIINGO_TICKERS_FILE"),
    ],
)
def test_tiingo_scheduler_env_var_exist(
    version, environment, terraform_output, env_var
):
    lambda_function_name = terraform_output["tiingo_scheduler_name"]["value"]
    region = terraform_output["region"]["value"]

    lambda_function_setup_contain_env_var(lambda_function_name, region, env_var)


@pytest.mark.parametrize(
    "event_rule, json_param",
    [
        (
            "Monday_to_Friday_8pm_HKT",
            '{"filters": [{"exchange": "SHE"}, {"exchange": "SHG"}]}',
        )
    ],
)
def test_target_has_right_param_for_rule(
    terraform_output, environment, event_rule: str, json_param: str
):
    lambda_function_arn = terraform_output["tiingo_scheduler_arn"]["value"]
    region = terraform_output["region"]["value"]
    events_client = boto3.client("events", region_name=region)  # type: botostubs.Events
    targets = events_client.list_targets_by_rule(Rule=f"{event_rule}_{environment}")

    assert len(targets["Targets"]) == 1
    assert targets["Targets"][0]["Arn"] == lambda_function_arn
    assert targets["Targets"][0]["Input"] == json_param


@pytest.mark.parametrize(
    "json_filter,expect_items",
    [
        (
            '[{"exchange": "NASDAQ", "asset_type": "Mutual Fund"}]',
            [
                "BVNSC",
                "CGVIC",
                "CIVEC",
                "CRUSC",
                "EMFN",
                "EMMT",
                "EVGBC",
                "EVLMC",
                "EVSTC",
                "EWJE",
                "FEFN",
                "FOANC",
                "IVENC",
                "IVFGC",
                "MOGLC",
                "NUCL",
                "PETZC",
                "RPIBC",
                "SRRIX",
                "XBGIOX",
                "XJEMDX",
            ],
        )
    ],
)
def test_lambda_trigger_is_sqs(
    terraform_output, json_filter: str, expect_items: List[str]
):
    region = terraform_output["region"]["value"]
    lambda_function_arn = terraform_output["tiingo_scheduler_name"]["value"]
    s3_bucket_name = terraform_output["s3_bucket_name"]["value"]
    base_path = "market_data_tiingo_scheduler"

    event = {"base_path": base_path, "filters": json.loads(json_filter)}

    payload = json.dumps(event)

    client_lambda = boto3.client("lambda", region_name=region)
    invoke_result = client_lambda.invoke(
        FunctionName=lambda_function_arn,
        InvocationType="RequestResponse",
        Payload=payload,
    )

    assert 200 == invoke_result["StatusCode"]

    start_time = datetime.now()
    max_wait_time_s = 240
    result_file_keys = set(
        [f"{base_path}/{ticker}/1d/data.csv" for ticker in expect_items]
    )

    while True:
        file_keys = set(
            get_matching_s3_keys(s3_bucket_name, f"{base_path}/", "data.csv")
        )

        if len(file_keys) == len(result_file_keys):
            break

        loop_time = datetime.now()
        if (loop_time - start_time).seconds > max_wait_time_s:
            assert False, f"Max wait time greater than {max_wait_time_s}s"

    assert result_file_keys == file_keys
