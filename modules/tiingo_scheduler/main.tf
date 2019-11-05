locals {
  module_name   = "tiingo_scheduler"
  zip_file_path = "lambda/${local.module_name}/${var.shopper_global.version}/package.zip"
}

resource "aws_lambda_function" "tiingo_scheduler_lambda_function" {
  function_name = lower(terraform.workspace) == "prod" ? local.module_name : "${local.module_name}_${var.shopper_global.environment}"
  handler       = "${local.module_name}.handler.handler"
  s3_bucket     = var.shopper_global.S3_lambda_bucket
  s3_key        = local.zip_file_path
  role          = aws_iam_role.tiingo_scheduler_lambda.arn
  runtime       = "python3.7"
  //  source_code_hash = filebase64sha256(local.zip_file_path)
  timeout = "300"

  tags = {
    version = var.shopper_global.version
    environment = var.shopper_global.environment
  }

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

resource "aws_cloudwatch_event_rule" "tiingo_scheduler" {
  for_each = var.tiingo_cron_setup

  name = each.key
  description         = each.key
  schedule_expression = each.value.cron
  tags = {
    version = var.shopper_global.version
    environment = var.shopper_global.environment
  }
}

resource "aws_cloudwatch_event_target" "tiingo_scheduler" {
  for_each = var.tiingo_cron_setup

  rule      = aws_cloudwatch_event_rule.tiingo_scheduler[each.key].name
  target_id = "trigger_${each.key}"
  arn       = aws_lambda_function.tiingo_scheduler_lambda_function.arn
  input     = each.value.filter_input
  tags = {
    version = var.shopper_global.version
    environment = var.shopper_global.environment
  }
}

resource "aws_lambda_permission" "tiingo_scheduler" {
  for_each = var.tiingo_cron_setup

  statement_id  = "AllowExecutionFromCloudWatch_${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tiingo_scheduler_lambda_function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.tiingo_scheduler[each.key].arn
}