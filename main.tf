terraform {
  required_version = ">= 0.12.6"
  required_providers {
    aws = "~> 2.8"
  }
}

//locals {
//  tiingo_ticker_file_path = var.tiingo_tickers_file_path
//  //  share_variable = {
//  //    version      = var.module_version
//  //    environment  = var.environment
//  //    region       = var.region
//  //    loging_level = var.loging_level
//  //  }
//}


module "tiingo_fetcher" {
  source                = "./modules/tiingo_fetcher"
  s3_market_data_bucket = var.S3_market_data_bucket
  tiingo_api_key        = var.tiingo_api_key
  shopper_global = var.shopper_global
}

module "tiingo_scheduler" {
  source                   = "./modules/tiingo_scheduler"
  shopper_global = var.shopper_global
  s3_market_data_bucket    = var.S3_market_data_bucket
  tiingo_tickers_file_path = var.tiingo_tickers_file_key
  tiingo_fetcher_arn       = module.tiingo_fetcher.arn
}

