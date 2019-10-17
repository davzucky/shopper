locals {
  module_name   = "tiingo_scheduler"
  zip_file_path = "lambda/${local.module_name}/${var.shopper_global.version}/package.zip"
}

resource "aws_lambda_function" "tiingo_scheduler_lambda_function" {
  function_name    = lower(terraform.workspace) == "prod" ? local.module_name : "${local.module_name}_${var.shopper_global.environment}"
  handler          = "${local.module_name}.handler.handler"
  s3_bucket        = var.shopper_global.S3_lambda_bucket
  s3_key           = local.zip_file_path
  role             = aws_iam_role.tiingo_scheduler_lambda.arn
  runtime          = "python3.7"
//  source_code_hash = filebase64sha256(local.zip_file_path)
  timeout          = "300"

  environment {
    variables = {
      "AWS_S3_BUCKET"                = var.s3_market_data_bucket
      "LAMBDA_INVOCATION_TYPE"       = "Event"
      "TIINGO_TICKERS_FILE"          = var.tiingo_tickers_file_path
      "LAMBDA_LOGGING_LEVEL"         = var.shopper_global.loging_level
      "TIINGO_FETCHER_FUNCTION_NAME" = var.tiingo_fetcher_arn
    }
  }
}

resource "aws_cloudwatch_event_rule" "Every_day_HK_8pm" {
  name                = lower(terraform.workspace) == "prod" ? "Monday_to_Friday_8pm_HKT" : "Monday_to_Friday_8pm_HKT_${var.shopper_global.environment}"
  description         = "Monday to Friday 8pm HKT"
  schedule_expression = "cron(0 12 ? * TUE-SAT *)"
}

resource "aws_cloudwatch_event_target" "run_tiingo_scheduler_Every_day_HK_8pm" {
  rule      = aws_cloudwatch_event_rule.Every_day_HK_8pm.name
  target_id = "Load_HK_Market_Data"
  arn       = aws_lambda_function.tiingo_scheduler_lambda_function.arn
  input     = "{\"filters\": [{\"exchange\": \"SHE\"}, {\"exchange\": \"SHG\"}]}"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_tiingo_scheduler" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tiingo_scheduler_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.Every_day_HK_8pm.arn
}