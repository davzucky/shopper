locals {
  region = "eu-west-3"
}

terraform {
  required_version = ">= 0.12.0"

  backend "s3" {
    region         = "ap-southeast-1"
    bucket         = "hwcom-prod-terraform-master-state"
    key            = "shopper/tiingo/ci_testing/terraform.tfstate"
    dynamodb_table = "hwcom-prod-terraform-master-state-lock"
    encrypt        = true

//    bucket         = "programmableproductioncom-dev-shopper-state"
//    key            = "testing/tiingo_fetcher/terraform.tfstate"
//    dynamodb_table = "programmableproductioncom-dev-shopper-state-lock"
//    encrypt        = true
  }
}

provider "aws" {
  region = "${local.region}"
  version = "~> 2.0"
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
  receive_wait_time_seconds = 20
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