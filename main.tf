terraform {
  required_version = ">= 0.12.6"
  required_providers {
    aws = "~> 2.8"
  }
}

module "tiingo_fetcher" {
  source                = "./modules/tiingo_fetcher"
  shopper_global        = var.shopper_global
  S3_lambda_bucket      = var.S3_lambda_bucket
  s3_market_data_bucket = var.S3_market_data_bucket
  tiingo_api_key        = var.tiingo_api_key
}

module "tiingo_scheduler" {
  source                   = "./modules/tiingo_scheduler"
  shopper_global           = var.shopper_global
  S3_lambda_bucket         = var.S3_lambda_bucket
  s3_market_data_bucket    = var.S3_market_data_bucket
  tiingo_tickers_file_path = var.tiingo_tickers_file_key
  tiingo_fetcher_arn       = module.tiingo_fetcher.arn
}

