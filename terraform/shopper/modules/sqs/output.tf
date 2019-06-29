output "sqs_tiingo_fetcher_arn" {
  value = "${aws_sqs_queue.tiingo_fetcher_fetch_queue.arn}"
}