// Share Variables. This are variable that are usually common and shared
variable "shopper_global" {
  type = object({
    version      = string
    environment  = string
    loging_level = string
    region       = string
  })
}

variable "S3_lambda_bucket" {
  type        = "string"
  description = "URL of the S3 lambda package store"
}

// Module specific variables
variable "s3_market_data_bucket" {
  type        = "string"
  description = "The name of the S3 storage where the market data has to be saved"
}

variable "tiingo_api_key" {
  type        = "string"
  description = "tiingo api key to use"
}
