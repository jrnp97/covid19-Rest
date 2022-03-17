# variables.tf to define module inputs

# HEROKU Vars
variable "heroku_email" {
  description = "Email associated with your heroku account"
  type = string
}

variable "heroku_api_key" {
  description = "Heroku Account API Key"
  type = string
}

# REPO Vars

variable "repo_project" {
  default = "jrnp97/covid19-Rest"
}

variable "repo_branch" {
  default = "heroku"
}

