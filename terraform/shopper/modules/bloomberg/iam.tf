resource "aws_iam_role" "bloomberg_lambda" {
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

resource "aws_iam_role_policy_attachment" "bloomberg_lambda" {
  policy_arn = "${aws_iam_policy.bloomberg_lambda.arn}"
  role = "${aws_iam_role.bloomberg_lambda.name}"
}

resource "aws_iam_policy" "bloomberg_lambda" {
  policy = "${data.aws_iam_policy_document.bloomberg_lambda.json}"
}

data "aws_iam_policy_document" "bloomberg_lambda" {
  statement {
    sid       = "AllowSQSPermissions"
    effect    = "Allow"
    resources = ["arn:aws:sqs:*"]

    actions = [
      "sqs:ChangeMessageVisibility",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes",
      "sqs:ReceiveMessage",
    ]
  }

  statement {
    sid       = "AllowInvokingLambdas"
    effect    = "Allow"
    resources = ["arn:aws:lambda:${var.aws_region_name}:*:function:*"]
    actions   = ["lambda:InvokeFunction"]
  }

  statement {
    sid       = "AllowCreatingLogGroups"
    effect    = "Allow"
    resources = ["arn:aws:logs:${var.aws_region_name}:*:*"]
    actions   = ["logs:CreateLogGroup"]
  }
  statement {
    sid       = "AllowWritingLogs"
    effect    = "Allow"
    resources = ["arn:aws:logs:${var.aws_region_name}:*:log-group:/aws/lambda/*:*"]

    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
  }
}