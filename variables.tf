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
    version      = string
    environment  = string
    loging_level = string
    region       = string
  })
  description = "Shopper shared global variables"
}

variable "s3_lambda_bucket" {
  type        = "string"
  description = "url of the s3 bucket that contain the lambda packages"
  default     = "hyperwave-research-modules-store"
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

variable "tiingo_cron_setup" {
  type        = "map"
  description = "Tiingo cron setup"
  default = {
    "SHEExchanges" = {
      cron         = "cron(0 14 ? * MON-FRI *)"
      filter_input = "{\"filters\": [{\"exchange\": \"SHE\"}]}"
    }
    "SHGExchanges" = {
      cron         = "cron(30 14 ? * MON-FRI *)"
      filter_input = "{\"filters\": [{\"exchange\": \"SHG\"}]}"
    }
    "NASDAQExchanges" = {
      cron         = "cron(0 2 ? * TUE-SAT *)"
      filter_input = "{\"filters\": [{\"exchange\": \"NASDAQ\"}]}"
    }
    "NYSEExchanges" = {
      cron         = "cron(30 2 ? * TUE-SAT *)"
      filter_input = "{\"filters\": [{\"exchange\": \"NYSE\"}]}"
    }
    "NYSEARCAExchanges" = {
      cron         = "cron(0 4 ? * TUE-SAT *)"
      filter_input = "{\"filters\": [{\"exchange\": \"NYSE ARCA\"}]}"
    }
  }
}

