locals {
  module_name = "tiingo_scheduler"
  zip_file_path = "${path.module}/../../packages/${local.module_name}.${var.share_variables.version}.zip"
}

resource "aws_lambda_function" "tiingo_scheduler_lambda_function" {
  function_name = "${local.module_name}_${var.share_variables.environment}"
  handler       = "${local.module_name}.handler.handler"
  filename      = local.zip_file_path
  role          = aws_iam_role.tiingo_scheduler_lambda.arn
  runtime       = "python3.7"
  source_code_hash = filebase64sha256(local.zip_file_path)
  timeout = "300"
  tags = {
    version = var.share_variables.version
  }

  environment {
    variables = {
      "AWS_S3_BUCKET" = var.s3_market_data_bucket
      "TIINGO_FETCHER_QUEUE" = var.trigger_sqs_arn
      "TIINGO_TICKERS_FILE" = var.tiingo_tickers_file_path
      "LAMBDA_LOGGING_LEVEL" = var.share_variables.loging_level
    }
  }
}

resource "aws_cloudwatch_event_rule" "Every_day_HK_8pm" {
    name = "Monday_to_Friday_8pm_HKT"
    description = "Monday to Friday 8pm HKT"
    schedule_expression = "cron(0 12 ? * TUE-SAT *)"
}

resource "aws_cloudwatch_event_target" "run_tiingo_scheduler_Every_day_HK_8pm" {
    rule = aws_cloudwatch_event_rule.Every_day_HK_8pm.name
    target_id = "Load_HK_Market_Data"
    arn = aws_lambda_function.tiingo_scheduler_lambda_function.arn
    input = "[{\"exchange\": \"SHE\"}, {\"exchange\": \"SHG\"}]"
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_tiingo_scheduler" {
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.tiingo_scheduler_lambda_function.function_name
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.Every_day_HK_8pm.arn
}