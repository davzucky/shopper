terraform {
  required_version = ">= 0.11.3"
}

provider "aws" {
  region = "ap-southeast-1"
}

module "terraform_state_backend" {
  source        = "git::https://github.com/cloudposse/terraform-aws-tfstate-backend.git?ref=master"
  namespace     = "programmableproduction.com"
  stage         = "dev"
  name          = "shopper"
  attributes    = ["state"]
  region        = "ap-southeast-1"
}

output "dynamodb_table_arn" {
  value = "${module.terraform_state_backend.dynamodb_table_arn}"
}

output "dynamodb_table_id" {
  value = "${module.terraform_state_backend.dynamodb_table_id}"
}

output "dynamodb_table_name" {
  value = "${module.terraform_state_backend.dynamodb_table_name}"
}

output "s3_bucket_arn" {
  value = "${module.terraform_state_backend.s3_bucket_arn}"
}

output "s3_bucket_domain_name" {
  value = "${module.terraform_state_backend.s3_bucket_domain_name}"
}

output "s3_bucket_id" {
  value = "${module.terraform_state_backend.s3_bucket_id}"
}