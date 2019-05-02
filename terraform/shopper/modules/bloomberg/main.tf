locals {
  module_name = "bloomberg"
  zip_file_path = "${var.packages_path}/${local.module_name}.${var.module_version}.zip"
}

resource "aws_lambda_function" "bloomberg_lambda_function" {
  function_name = "bloomberg"
  handler       = "bloomberg.handler.handler"
  filename      = "${local.zip_file_path}"
  role          = "${aws_iam_role.bloomberg_lambda.arn}"
  runtime       = "python3.7"
  source_code_hash = "${base64sha256(file("${local.zip_file_path}"))}"

  environment {
    variables {
      "aws_s3_bucket" = "${var.s3_market_data_bucket}",
      "aws_region" = "${var.aws_region_name}"
    }
  }
}

resource "aws_lambda_event_source_mapping" "bloomberg_sqs_trigger" {
  batch_size        = 1
  event_source_arn  = "${var.trigger_sqs_arn}"
  enabled           = true
  function_name     = "${aws_lambda_function.bloomberg_lambda_function.arn}"
}
