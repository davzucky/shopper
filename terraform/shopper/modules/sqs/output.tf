output "tiingo_fetcher" {
  value = {
    "name" = aws_sqs_queue.tiingo_fetcher_fetch_queue.name
    "arn"  = aws_sqs_queue.tiingo_fetcher_fetch_queue.arn
  }
}