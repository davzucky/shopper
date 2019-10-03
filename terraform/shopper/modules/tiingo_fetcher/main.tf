locals {
  module_name   = "tiingo_fetcher"
  zip_file_path = "${path.module}/../../packages/${local.module_name}.${var.share_variables.version}.zip"
}

resource "aws_lambda_function" "tiingo_fetcher_lambda_function" {
  function_name    = lower(terraform.workspace) == "prod" ? local.module_name : "${local.module_name}_${var.share_variables.environment}"
  handler          = "tiingo_fetcher.handler.handler"
  filename         = local.zip_file_path
  role             = aws_iam_role.tiingo_fetcher_lambda.arn
  runtime          = "python3.7"
  source_code_hash = filebase64sha256(local.zip_file_path)
  timeout          = "300"
  tags = {
    version = var.share_variables.version
  }

  environment {
    variables = {
      "AWS_S3_BUCKET"        = var.s3_market_data_bucket
      "TIINGO_API_KEY"       = var.tiingo_api_key
      "LAMBDA_LOGGING_LEVEL" = var.share_variables.loging_level
    }
  }
}
