locals {
  module_name   = "tiingo_fetcher"
  zip_file_path = "lambda/${local.module_name}/${var.shopper_global.version}/package.zip"
}

resource "aws_lambda_function" "tiingo_fetcher_lambda_function" {
  function_name = lower(terraform.workspace) == "prod" ? local.module_name : "${local.module_name}_${var.shopper_global.environment}"
  handler       = "tiingo_fetcher.handler.handler"
  s3_bucket     = var.S3_lambda_bucket
  s3_key        = local.zip_file_path
  role          = aws_iam_role.tiingo_fetcher_lambda.arn
  runtime       = "python3.7"
  //  source_code_hash = filebase64sha256(local.zip_file_path)
  timeout = "300"
  tags = {
    version = var.shopper_global.version
  }

  environment {
    variables = {
      "AWS_S3_BUCKET"        = var.s3_market_data_bucket
      "TIINGO_API_KEY"       = var.tiingo_api_key
      "LAMBDA_LOGGING_LEVEL" = var.shopper_global.loging_level
    }
  }
}
