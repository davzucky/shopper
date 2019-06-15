locals {
  region = "eu-west-3"
}

terraform {
  required_version = ">= 0.11.14"
}

provider "aws" {
  region = "${local.region}"
  version = "~> 2.0"
}

resource "random_string" "test" {
  # Generate a random id for each deployment
  length = 8
  override_special = "-"
}

resource "aws_s3_bucket" "test_tiingo" {
  bucket = "market-data-${lower(random_string.test.result)}"
  region = "${local.region}"
}

resource "aws_sqs_queue" "test_tiingo" {
  name = "tiingo_fetch-${lower(random_string.test.result)}"
  visibility_timeout_seconds = "300"
  receive_wait_time_seconds = 20
}

resource "aws_s3_bucket_object" "tiingo_ticker_csv" {
  bucket = "${aws_s3_bucket.test_tiingo.bucket}"
  key = "${var.tiingo_tickers_path}"
  source = "supported_tickers.csv"
}

module "tiingo_scheduler" {
  source = "../../../shopper/modules/tiingo_scheduler"
  aws_region_name = "${local.region}"
  module_version = "${var.module_version}"
  packages_path = "../../../shopper/packages"
  s3_market_data_bucket = "${aws_s3_bucket.test_tiingo.bucket}"
  trigger_sqs_arn = "${aws_sqs_queue.test_tiingo.name}"
  tiingo_tickers_file_path = "${var.tiingo_tickers_path}"
  loging_level = "DEBUG"
}

variable "module_version" {
  type = "string"
  description = "version of the module"
}

variable "tiingo_tickers_path" {
  default = "static/tiingo_tickers.csv"
  type = "string"
  description = "Path to the tiingo tickers csv file"
}

output "sqs_queue_name" {
  value = "${aws_sqs_queue.test_tiingo.name}"
}

output "s3_bucket_name" {
  value = "${aws_s3_bucket.test_tiingo.bucket}"
}

output "lambda_function_name" {
  value = "${module.tiingo_scheduler.function_name}"
}

output "lambda_function_arn" {
  value = "${module.tiingo_scheduler.lambda_arn}"
}

output "region" {
  value = "${local.region}"
}