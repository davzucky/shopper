terraform {
  required_version = ">= 0.12.6"
}

provider "aws" {
  region  = var.aws_region
  version = "~> 2.0"
}

resource "aws_s3_bucket" "test_tiingo" {
  bucket        = var.s3_bucker_name
  region        = var.aws_region
  force_destroy = true
}

resource "aws_s3_bucket_object" "tickers" {
  bucket = aws_s3_bucket.test_tiingo.bucket
  key    = "static/tiingo_tickers.csv"
  source = "${path.module}/supported_tickers.csv"
  depends_on  = [aws_s3_bucket_object.tiingo_fetcher_lambda_package,
                 aws_s3_bucket_object.tiingo_scheduler_lambda_package]

}

resource "aws_s3_bucket_object" "tiingo_fetcher_lambda_package" {
  bucket = aws_s3_bucket.test_tiingo.bucket
  key    = "lambda/tiingo_fetcher/${var.module_version}/package.zip"
  source = "${path.module}/../../../packages/tiingo_fetcher.${var.module_version}.zip"
}

resource "aws_s3_bucket_object" "tiingo_scheduler_lambda_package" {
  bucket = aws_s3_bucket.test_tiingo.bucket
  key    = "lambda/tiingo_scheduler/${var.module_version}/package.zip"
  source = "${path.module}/../../../packages/tiingo_scheduler.${var.module_version}.zip"
}

module "shopper" {
  source = "../../../"
  shopper_global = {
    version          = var.module_version
    environment      = var.environment
    region           = var.aws_region
    loging_level     = "DEBUG"
    S3_lambda_bucker = aws_s3_bucket.test_tiingo.bucket
  }

  tiingo_tickers_file_path = aws_s3_bucket_object.tickers.key
  S3_market_data_bucket    = aws_s3_bucket.test_tiingo.bucket
  tiingo_api_key           = var.tiingo_api_key
}
