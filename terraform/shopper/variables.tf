variable "environment" {
  type        = "string"
  description = "Name of the environment where the module is deployed"
}

variable "loging_level" {
  type        = "string"
  description = "Login level to set for all modules"
  default     = "INFO"
}

variable "region" {
  type        = "string"
  description = "Name of the region where the market data bucket is located "
}

variable "S3_market_data_bucket" {
  type        = "string"
  description = "Name of the bucket that handle the market data"
}

variable "scope" {
  type        = "string"
  description = "Scope name that will be happen to all object created. Default value test. Blank is allow to prod deployement"
  default     = "test"
}

variable "tiingo_api_key" {
  type        = "string"
  description = "Tiingo API key to use"
}

variable "tiingo_tickers_file_path" {
  type        = "string"
  description = "Tiingo path to the file containing the tickers"
  default     = "static/tiingo_tickers.csv"
}

