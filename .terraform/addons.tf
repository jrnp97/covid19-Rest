# ref: https://elements.heroku.com/addons/cleardb

# ref: https://elements.heroku.com/addons/heroku-postgresql
resource "heroku_addon" "api_database" {
  app  = heroku_app.api_app.name
  plan = "heroku-postgresql:hobby-dev"
}

# ref: https://elements.heroku.com/addons/logtail
resource "heroku_addon" "api_logs" {
  app = heroku_app.api_app.name
  plan = "logtail:free"
}

# ref: https://elements.heroku.com/addons/cloudamqp
resource "heroku_addon" "api_rabbitmq" {
  app  = heroku_app.api_app.name
  plan = "cloudamqp:lemur"
}
