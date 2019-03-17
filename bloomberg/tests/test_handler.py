def get_sample_sqs_message(ticker: str, s3_bucket: str, file_key: str):
    return {
        "Records": [
            {
                "messageId": "c80e8021-a70a-42c7-a470-796e1186f753",
                "receiptHandle": "EMPTY",
                "body": '{"foo":"bar"}',
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
