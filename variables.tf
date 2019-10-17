//variable "environment" {
//  type        = "string"
//  description = "Name of the environment where the module is deployed"
//}
//
//variable "module_version" {
//  type = "string"
//  description = "version of the module"
//  default = "local"
//}
//
//variable "loging_level" {
//  type        = "string"
//  description = "Login level to set for all modules"
//  default     = "INFO"
//}
//
//variable "region" {
//  type        = "string"
//  description = "Name of the region where the market data bucket is located"
//}

variable "shopper_global" {
  type = object({
    version          = string
    environment      = string
    loging_level     = string
    region           = string
    S3_lambda_bucket = string
  })
  description = "Shopper shared global variables"
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

