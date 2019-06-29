resource "aws_sqs_queue" "tiingo_fetcher_fetch_queue" {
  name = "tiingo_fetcher_fetch_${var.share_variables.environment}"

  visibility_timeout_seconds = "300"
  receive_wait_time_seconds = 20
}