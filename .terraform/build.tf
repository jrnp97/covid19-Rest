# Module to define building resources

# Building the repo code [this avoid the heroku formation error "Couldn't find that process type (web)"]
resource "heroku_build" "api_source_code" {
  app = heroku_app.api_app.name

  source {
    url = "https://github.com/${var.repo_project}/tarball/${var.repo_branch}"
  }

}


resource "heroku_formation" "api_dyno_config" {
  app      = heroku_app.api_app.name
  type     = "web"
  quantity = "1"
  size     = "free"

  depends_on = [
    heroku_build.api_source_code
  ]
}