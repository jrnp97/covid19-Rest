# apps.tf file to configure heroku apps

resource "heroku_app" "api_app" {
  name = "api-oscloud"

  buildpacks = [
    "https://github.com/heroku/heroku-buildpack-python.git"
  ]

  region = "us"
  stack  = "heroku-20"
  acm    = false

}