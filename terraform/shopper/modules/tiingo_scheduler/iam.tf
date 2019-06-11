resource "aws_iam_role" "tiingo_scheduler_lambda" {
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "tiingo_scheduler_lambda" {
  policy_arn = "${aws_iam_policy.bloomberg_lambda.arn}"
  role = "${aws_iam_role.tiingo_scheduler_lambda.name}"
}

resource "aws_iam_policy" "bloomberg_lambda" {
  policy = "${data.aws_iam_policy_document.tiingo_scheduler_lambda.json}"
}

data "aws_iam_policy_document" "tiingo_scheduler_lambda" {
  statement {
    sid = "AllowSQSPermissions"
    effect = "Allow"
    resources = [
      "arn:aws:sqs:*"]

    actions = [
      "sqs:SendMessage",
      "sqs:SendMessageBatch",
      "sqs:ChangeMessageVisibility",
      "sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
    ]
  }

  statement {
    sid = "AllowInvokingLambdas"
    effect = "Allow"
    resources = [
      "arn:aws:lambda:${var.aws_region_name}:*:function:*"]
    actions = [
      "lambda:InvokeFunction"]
  }

  statement {
    sid = "AllowCreatingLogGroups"
    effect = "Allow"
    resources = [
      "arn:aws:logs:${var.aws_region_name}:*:*"]
    actions = [
      "logs:CreateLogGroup"]
  }

  statement {
    sid = "AllowWritingLogs"
    effect = "Allow"
    resources = [
      "arn:aws:logs:${var.aws_region_name}:*:log-group:/aws/lambda/*:*"]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
  statement {
    sid = "AllowS3Access"
    effect = "Allow"
    resources = [
      "arn:aws:s3:::${var.s3_market_data_bucket}",
      "arn:aws:s3:::${var.s3_market_data_bucket}/*"
    ]
    actions = [
      "s3:*"
    ]
  }
}