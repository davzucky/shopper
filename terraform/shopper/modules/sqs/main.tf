
resource "aws_sqs_queue" "bloomberg_fetch_queue" {
  name = "bloomberg_fetch"
}

resource "aws_sqs_queue" "tiingo_fetcher_fetch_queue" {
  name = "tiigo_fetcher_fetch"
}