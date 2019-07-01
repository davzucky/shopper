locals {
  tiingo_ticker_file_path = "static/tinngo_tickers.csv"
  share_variable = {
    version      = var.module_version
    environment  = var.environment
    region       = var.region
    loging_level = var.loging_level
  }
}

// Disable Bloomberg for the moment because of problem with request from AWS
//module "bloomberg" {
//  source = "./modules/bloomberg"
//  packages_path = "${local.packages_path}"
//  s3_market_data_bucket = "${var.S3_market_data_bucket}"
//  aws_region_name= "${var.S3_market_data_region}"
//  trigger_sqs_arn = "${module.sqs.sqs_bloomberg_arn}"
//  module_version = "${var.module_version}"
//}


module "sqs" {
  source          = "./modules/sqs"
  share_variables = local.share_variable
}

module "tiingo_fetcher" {
  source                = "./modules/tiingo_fetcher"
  s3_market_data_bucket = var.S3_market_data_bucket
  trigger_sqs_arn       = module.sqs.tiingo_fetcher.arn
  tiingo_api_key        = var.tiingo_api_key
  share_variables       = local.share_variable
}

module "tiingo_scheduler" {
  source                   = "./modules/tiingo_scheduler"
  share_variables          = local.share_variable
  s3_market_data_bucket    = var.S3_market_data_bucket
  tiingo_tickers_file_path = local.tiingo_ticker_file_path
  trigger_sqs_arn          = module.sqs.tiingo_fetcher.name
}

