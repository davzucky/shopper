variable "module_version" {
  type        = "string"
  description = "version of the module"
}

variable "s3_bucket_name" {
  type        = "string"
  description = "Name of the s3 bucker used for the test"
}

variable "tiingo_api_key" {
  type        = "string"
  description = "Tiingo api Key"
}

variable "aws_region" {
  type        = "string"
  description = "aws region where to deploy"
}

variable "environment" {
  type        = "string"
  description = "Name of the environmenet"
}
