import os

import pytest
from datetime import datetime, date, time
from typing import Dict, Any

from ..message import Message
from ..aws import download_file_from_S3_to_temp, get_ohcl_row_str
from .test_bloomberg import set_request_mock_valid_data
from .test_aws import do_test_setup, BUCKET, REGION_NAME, SAMPLE_CONTENT
from ..handler import AWS_S3_BUCKET, AWS_REGION, handler


def test_when_wrong_ticker_does_not_change_file(
    tmpdir, monkeypatch, requests_mock, caplog
):
    # Setup the file in S3
    with do_test_setup():
        # Setup the required env variable
        monkeypatch.setenv(AWS_S3_BUCKET, BUCKET)
        monkeypatch.setenv(AWS_REGION, REGION_NAME)

        ticker = "UNKNOW"

        from bloomberg.tests import test_bloomberg

        test_bloomberg.set_request_mock_unknown_ticker(requests_mock, ticker)

        # setup the message
        sqs_message = get_sample_sqs_message(ticker, "/marketdata/test/1d/data.csv")
        handler(sqs_message, None)

        # Check that the message "Error loading data from Bloomberg" is warning level
        # and see 1
        nb_warning_message = 0
        for record in caplog.records:
            if record.message.startswith("Error loading data from Bloomberg"):
                nb_warning_message += 1
                assert record.levelname == "WARNING"
        assert nb_warning_message == 1


@pytest.mark.parametrize(
    "env_values,env_var_to_error",
    [
        ({AWS_S3_BUCKET: "TEST_BUCKET"}, AWS_REGION),
        ({AWS_REGION: "us-east-1"}, AWS_S3_BUCKET),
    ],
)
def test_error_and_exit_with_1_(
    env_values: Dict[str, str], env_var_to_error: str, monkeypatch, caplog
):
    for var_name, var_value in env_values.items():
        monkeypatch.setenv(var_name, var_value)

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        ticker = "UNKNOW"
        # setup the message
        sqs_message = get_sample_sqs_message(ticker, "/marketdata/test/1d/data.csv")
        handler(sqs_message, None)
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == -1
    nb_error_messages = 0
    expected_message = "The environement variable {} is not set.".format(
        env_var_to_error
    )
    for record in caplog.records:
        if expected_message in record.message:
            nb_error_messages += 1
            assert record.levelname == "ERROR"
    assert nb_error_messages == 1


def test_handler_update_s3_file_that_exist_add_new_row(
    tmpdir, monkeypatch, requests_mock, caplog
):
    bucket_name = "another_bucket"
    region_name = "us-east-1"
    file_key = "/marketdata/test/1d/data.csv"
    file_content = SAMPLE_CONTENT
    ticker = "JPMPCAA:HK"
    price = 213.5
    price_date = date(2019, 1, 4)
    tmp_file_name = "file_to_check.csv"

    # Setup the file in S3
    with do_test_setup(bucket_name, region_name, file_key, file_content):
        # Setup the required env variable
        monkeypatch.setenv(AWS_S3_BUCKET, bucket_name)
        monkeypatch.setenv(AWS_REGION, region_name)

        set_request_mock_valid_data(
            requests_mock, ticker, price, datetime.combine(price_date, time(6, 0, 0))
        )

        # setup the message
        sqs_message = get_sample_sqs_message(ticker, file_key)
        handler(sqs_message, None)

        tmp_path = os.path.join(tmpdir.dirname, tmp_file_name)
        download_file_from_S3_to_temp(region_name, bucket_name, file_key, tmp_path)

        new_file_content = open(tmp_path, "r").read()
        new_row_str = get_ohcl_row_str(price_date, price, price, price, price)

        assert new_file_content == "{}{}".format(file_content, new_row_str)


def get_sample_sqs_message(ticker: str, file_key: str) -> Dict[str, Any]:
    message = Message(ticker, file_key)
    #
    return {
        "Records": [
            {
                "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                "receiptHandle": "EMPTY",
                "body": message.to_json(),
                "attributes": {
                    "ApproximateReceiveCount": "3",
                    "SentTimestamp": "1529104986221",
                    "SenderId": "594035263019",
                    "ApproximateFirstReceiveTimestamp": "1529104986230",
                },
                "messageAttributes": {},
                "md5OfBody": "9bb58f26192e4ba00f01e2e7b136bbd8",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-west-2:594035263019:NOTFIFOQUEUE",
                "awsRegion": "us-west-2",
            }
        ]
    }
