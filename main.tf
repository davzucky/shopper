terraform {
  required_version = ">= 0.12.11"
  required_providers {
    aws = "~> 2.8"
  }
}

module "tiingo_fetcher" {
  source                = "./modules/tiingo_fetcher"
  s3_market_data_bucket = var.S3_market_data_bucket
  s3_lambda_bucket      = var.s3_lambda_bucket
  tiingo_api_key        = var.tiingo_api_key
  shopper_global        = var.shopper_global
}

module "tiingo_scheduler" {
  source                   = "./modules/tiingo_scheduler"
  shopper_global           = var.shopper_global
  s3_lambda_bucket         = var.s3_lambda_bucket
  s3_market_data_bucket    = var.S3_market_data_bucket
  tiingo_tickers_file_path = var.tiingo_tickers_file_key
  tiingo_fetcher_arn       = module.tiingo_fetcher.arn
  tiingo_cron_setup        = var.tiingo_cron_setup
}

