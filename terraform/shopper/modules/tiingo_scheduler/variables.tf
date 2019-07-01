// Share Variables. This are variable that are usually common and shared
variable "share_variables" {
  type = object({
    version = string
    environment = string
    region = string
    loging_level = string
  })
}

// Module specific variables

variable "s3_market_data_bucket" {
  type = "string"
  description = "The name of the S3 storage where the market data has to be saved"
}

variable "trigger_sqs_arn" {
  type = "string"
  description = "arn of the sqs queue that the trigger has to listen to"
}

variable "tiingo_tickers_file_path"  {
  type = "string"
  description = "Path to the tiingo tickers file in the s3 bucker"
  default = "static/tiingo_tickers.csv"
}

