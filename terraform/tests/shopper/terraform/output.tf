output "s3_bucket_name" {
  value = aws_s3_bucket.test_tiingo.bucket
}

output "region" {
  value = var.aws_region
}

output "tiingo_fetcher_name" {
  value = module.shopper.tiingo_fetcher_name
}

output "tiingo_fetcher_arn" {
  value = module.shopper.tiingo_fetcher_arn
}

output "tiingo_scheduller_name" {
  value = module.shopper.tiingo_scheduler_name
}

output "tiingo_scheduller_arn" {
  value = module.shopper.tiingo_scheduler_arn
}