locals {
  packages_path = "${path.module}/packages"
}

module "bloomberg" {
  source = "./modules/bloomberg"
  packages_path = "${local.packages_path}"
  s3_market_data_bucket = "${var.S3_market_data_bucket}"
  aws_region_name= "${var.S3_market_data_region}"
  trigger_sqs_arn = "${module.sqs.sqs_bloomberg_arn}"
  module_version = "${var.module_version}"
}


module "tiingo_fetcher" {
  source = "./modules/tiingo_fetcher"
  packages_path = "${local.packages_path}"
  s3_market_data_bucket = "${var.S3_market_data_bucket}"
  aws_region_name= "${var.S3_market_data_region}"
  trigger_sqs_arn = "${module.sqs.sqs_tiingo_fetcher_arn}"
  module_version = "${var.module_version}"
}

module "sqs" {
  source = "./modules/sqs"
}