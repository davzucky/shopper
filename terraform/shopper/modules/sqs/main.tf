resource "aws_sqs_queue" "tiingo_fetcher_fetch_queue" {
  name                       = lower(terraform.workspace) == "prod" ? "tiingo-fetcher-fetch" : "tiingo-fetcher-fetch-${var.share_variables.environment}"
  visibility_timeout_seconds = "300"
  receive_wait_time_seconds  = 20
}