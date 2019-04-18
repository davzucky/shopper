variable "S3_market_data_bucket" {
  type = "string"
  description = "Name of the bucket that handle the market data"
}

variable "S3_market_data_region" {
  type = "string"
  description = "Name of the region where the market data bucket is located "
}

variable "scope" {
  type = "string"
  description = "Scope name that will be happen to all object created. Default value test. Blank is allow to prod deployement"
  default = "test"
}