locals {
  module_name = "tiingo_fetcher"
  zip_file_path = "${var.packages_path}/${local.module_name}.${var.module_version}.zip"
}

resource "aws_lambda_function" "tiingo_fetcher_lambda_function" {
  function_name = "tiingo_fetcher"
  handler       = "tiingo_fetcher.handler.handler"
  filename      = "${local.zip_file_path}"
  role          = "${aws_iam_role.tiingo_fetcher_lambda.arn}"
  runtime       = "python3.7"
  source_code_hash = filebase64sha256("${local.zip_file_path}")
  timeout = "60"
  tags = {
    version = "${var.module_version}"
  }

  environment {
    variables = {
      "AWS_S3_BUCKET" = "${var.s3_market_data_bucket}",
      "TIINGO_API_KEY" = "${var.tiingo_api_key}"
    }
  }
}

resource "aws_lambda_event_source_mapping" "tiingo_fetcher_sqs_trigger" {
  batch_size        = 1
  event_source_arn  = var.trigger_sqs_arn
  enabled           = true
  function_name     = "${aws_lambda_function.tiingo_fetcher_lambda_function.arn}"
}
