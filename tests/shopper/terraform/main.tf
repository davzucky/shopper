terraform {
  required_version = ">= 0.12"
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
  source = "./supported_tickers.csv"
}

module "shopper" {
  source                   = "../../../"
  tiingo_tickers_file_path = aws_s3_bucket_object.tickers.key
  loging_level             = "DEBUG"
  environment              = var.environment
  region                   = var.aws_region
  S3_market_data_bucket    = aws_s3_bucket.test_tiingo.bucket
  tiingo_api_key           = var.tiingo_api_key
}




