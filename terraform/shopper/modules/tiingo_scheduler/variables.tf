variable "s3_market_data_bucket" {
  type = "string"
  description = "The name of the S3 storage where the market data has to be saved"
}

variable "aws_region_name" {
  type = "string"
  description = "The name the region where the s3 bucket is located"
}

variable "packages_path" {
  type = "string"
  description = "Path to the folder containing the packages"
}

variable "trigger_sqs_arn" {
  type = "string"
  description = "arn of the sqs queue that the trigger has to listen to"
}

variable "module_version" {
  type = "string"
  description = "Version of the module"
}

variable "loging_level" {
  type = "string"
  description = "Loging level for the lambda"
  default = "INFO"
}

variable "tiingo_tickers_file_path"  {
  type = "string"
  description = "Path to the tiingo tickers file in the s3 bucker"
  default = "static/tinngo_tickers.csv"
}