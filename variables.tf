
variable "shopper_global" {
  type = object({
    version      = string
    environment  = string
    loging_level = string
    region       = string
  })
  description = "Shopper shared global variables"
}

variable "S3_lambda_bucket" {
  type        = "string"
  description = "URL of the S3 storage that contain the lambda"
  default     = "s3://hw-modules-store"
}

variable "S3_market_data_bucket" {
  type        = "string"
  description = "Name of the bucket that handle the market data"
}

variable "tiingo_api_key" {
  type        = "string"
  description = "Tiingo API key to use"
}

variable "tiingo_tickers_file_key" {
  type        = "string"
  description = "Tiingo path to the file containing the tickers"
  default     = "static/tiingo_tickers.csv"
}

