locals {
  tiingo_ticker_file_path = var.tiingo_tickers_file_path
  share_variable = {
    version      = var.module_version
    environment  = var.environment
    region       = var.region
    loging_level = var.loging_level
  }
}


module "tiingo_fetcher" {
  source                = "./modules/tiingo_fetcher"
  s3_market_data_bucket = var.S3_market_data_bucket
  tiingo_api_key        = var.tiingo_api_key
  share_variables       = local.share_variable
}

module "tiingo_scheduler" {
  source                   = "./modules/tiingo_scheduler"
  share_variables          = local.share_variable
  s3_market_data_bucket    = var.S3_market_data_bucket
  tiingo_tickers_file_path = local.tiingo_ticker_file_path
  tiingo_fetcher_arn       = module.tiingo_fetcher.arn
}

