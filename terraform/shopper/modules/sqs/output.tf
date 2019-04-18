output "sqs_bloomberg_arn" {
  value = "${aws_sqs_queue.bloomberg_fetch_queue.arn}"
}