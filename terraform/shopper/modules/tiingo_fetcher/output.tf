//variable "shopper_version" {
//  default = "0.0.0"
//  description = "version of the module"
//  type = "string"
//}

output "function_name" {
  value = "${aws_lambda_function.tiingo_fetcher_lambda_function.function_name}"
}

