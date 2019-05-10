locals {
  region = "ap-southeast-1"
}

terraform {
  required_version = ">= 0.11.3"

  backend "s3" {
    region         = "ap-southeast-1"
    bucket         = "programmableproductioncom-dev-shopper-state"
    key            = "testing/tiingo_fetcher/terraform.tfstate"
    dynamodb_table = "programmableproductioncom-dev-shopper-state-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "${local.region}"
}

resource "random_string" "test" {
  # Generate a random id for each deployment
  length           = 8
  override_special = "-"
}

resource "aws_s3_bucket" "test_tiingo"{
  bucket = "market-data-${lower(random_string.test.result)}"
  region = "${local.region}"
}

resource "aws_sqs_queue" "test_tiingo" {
  name = "tiingo_fetch-${lower(random_string.test.result)}"
  visibility_timeout_seconds = "300"
}

module "tiingo_fetcher" {
  source = "../../../shopper/modules/tiingo_fetcher"
  aws_region_name = "${local.region}"
  module_version = "${var.module_version}"
  packages_path = "../../../shopper/packages"
  s3_market_data_bucket = "${aws_s3_bucket.test_tiingo.bucket}"
  tiingo_api_key = "${var.tiingo_api_key}"
  trigger_sqs_arn = "${aws_sqs_queue.test_tiingo.arn}"
}

variable "module_version" {
  type = "string"
  description = "version of the module"
  default = "0.1.81f4b54"
 }

variable "tiingo_api_key" {
  type = "string"
  description = "Tiingo api Key"
 }

output "sqs_queue_name" {
  value = "${aws_sqs_queue.test_tiingo.name}"
}


output "s3_bucket_name" {
  value = "${aws_s3_bucket.test_tiingo.bucket}"
}

output "lambda_function_name" {
  value = "${module.tiingo_fetcher.function_name}"
}

output "region" {
  value = "${local.region}"
}