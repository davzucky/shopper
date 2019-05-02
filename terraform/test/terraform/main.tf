locals {
  region = "eu-west-3"
}

provider "aws" {
  region = "${local.region}"
}

resource "random_id" "test" {
  byte_length = 8
}

module "shopper" {
  source = "../../shopper"

  //  version = "0.1.0.1.2a1a748"
  //  module_version = "0.1.2a1a748"
  S3_market_data_bucket = "${aws_s3_bucket.test_market_data_bucket.bucket}"
//  S3_market_data_bucket = "${aws_s3_bucket.test_market_data_bucket.arn}"

  S3_market_data_region = "${aws_s3_bucket.test_market_data_bucket.region}"
}

resource "aws_s3_bucket" "test_market_data_bucket" {
  bucket = "market-data-${lower(random_id.test.b64_url)}"
  region = "${local.region}"
}
