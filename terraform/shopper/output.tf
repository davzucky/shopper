output "tiingo_fetcher_arn" {
  value = module.tiingo_fetcher.arn
  description = "Lambda tiingo fetcher arn"
}

output "tiingo_fetcher_name" {
  value = module.tiingo_fetcher.name
  description = "Lambda tiingo fetcher function name"
}

output "tiingo_scheduler_arn" {
  value = module.tiingo_scheduler.arn
  description = "Lambda tiingo scheduler arn"
}

output "tiingo_scheduler_name" {
  value = module.tiingo_fetcher.name
  description = "Lambda tiingo scheduler function name"
}

