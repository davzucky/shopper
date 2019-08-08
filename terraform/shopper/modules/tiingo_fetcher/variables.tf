// Share Variables. This are variable that are usually common and shared
variable "share_variables" {
  type = object({
    version      = string
    environment  = string
    loging_level = string
    region       = string
  })
}

// Module specific variables
variable "s3_market_data_bucket" {
  type        = "string"
  description = "The name of the S3 storage where the market data has to be saved"
}

variable "trigger_sqs_arn" {
  type        = "string"
  description = "arn of the sqs queue that the trigger has to listen to"
}

variable "tiingo_api_key" {
  type        = "string"
  description = "tiingo api key to use"
}
