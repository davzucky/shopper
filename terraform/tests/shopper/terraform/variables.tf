variable "module_version" {
  type        = "string"
  description = "version of the module"
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
