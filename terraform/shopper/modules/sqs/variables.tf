// Share Variables. This are variable that are usually common and shared
variable "share_variables" {
  type = object({
    version      = string
    environment  = string
    loging_level = string
    region       = string
  })
}

// Module specific variables
