from typing import Dict, Any

from bloomberg.tests import test_aws
from .test_aws import do_test_setup, BUCKET, REGION_NAME

from ..handler import AWS_S3_BUCKET, AWS_REGION, handler
from ..messages.bloomberg import BloombergMessage


def test_when_wrong_ticker_does_not_change_file(
    tmpdir, monkeypatch, requests_mock, caplog
):
    # Setup the file in S3
    with do_test_setup():
        # Setup the required env variable
        monkeypatch.setenv(AWS_S3_BUCKET, BUCKET)
        monkeypatch.setenv(AWS_REGION, REGION_NAME)

        ticker = "UNKNOW"
        from bloomberg.tests import test_aws

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

#
# def test_when_right_ticker_update_s3_file_that_exist_add_new_row(
#     tmpdir, monkeypatch, requests_mock, caplog
# ):
#     # Setup the file in S3
#     with do_test_setup():
#         # Setup the required env variable
#         monkeypatch.setenv(AWS_S3_BUCKET, BUCKET)
#         monkeypatch.setenv(AWS_REGION, REGION_NAME)
#
#         ticker = "JPMPCAA:HK"
#         test_aws.set_request_mock_valid_data(requests_mock, ticker)
#
#         # setup the message
#         sqs_message = get_sample_sqs_message(ticker, "/marketdata/test/1d/data.csv")
#         handler(sqs_message, None)
#
#         # Check that the message "Error loading data from Bloomberg" is
#         # warning level and see 1
#         nb_warning_message = 0
#         for record in caplog.records:
#             if record.message.startswith("Error loading data from Bloomberg"):
#                 nb_warning_message += 1
#                 assert record.levelname == "WARNING"
#         assert nb_warning_message == 1
#

def get_sample_sqs_message(ticker: str, file_key: str) -> Dict[str, Any]:
    message = BloombergMessage(ticker, file_key)
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
