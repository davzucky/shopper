output "sqs_bloomberg_arn" {
  value = "${aws_sqs_queue.bloomberg_fetch_queue.arn}"
}

output "sqs_tiingo_fetcher_arn" {
  value = "${aws_sqs_queue.tiingo_fetcher_fetch_queue.arn}"
}