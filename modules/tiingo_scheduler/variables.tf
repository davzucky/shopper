// Share Variables. This are variable that are usually common and shared
variable "shopper_global" {
  type = object({
    version          = string
    environment      = string
    loging_level     = string
    region           = string
    S3_lambda_bucket = string
  })
}

// Module specific variables

variable "tiingo_fetcher_arn" {
  type        = "string"
  description = "arn of the target lambda"
}

variable "s3_market_data_bucket" {
  type        = "string"
  description = "The name of the S3 storage where the market data has to be saved"
}

variable "tiingo_tickers_file_path" {
  type        = "string"
  description = "Path to the tiingo tickers file in the s3 bucker"
  default     = "static/tiingo_tickers.csv"
}

