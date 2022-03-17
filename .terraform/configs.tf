# Module to define heroku apps/addons configuration
locals {
  database = regex("postgres://(?P<user>.+):(?P<pwd>.+)@(?P<host>.+):(?P<port>\\d+)/(?P<db>\\w+)", heroku_addon.api_database.config_var_values.DATABASE_URL)
}

resource "heroku_app_config_association" "api_config" {
  app_id = heroku_app.api_app.id
  vars = {
    APP_URL = heroku_app.api_app.web_url
    DB_HOST = local.database.host
    DB_DATABASE = local.database.db
    DB_USERNAME = local.database.user
    DB_PORT = local.database.port
    #DISABLE_COLLECTSTATIC = 1
  }

  sensitive_vars = {
    DB_PASSWORD = local.database.pwd
    BROKER_URL = heroku_addon.api_rabbitmq.config_var_values.CLOUDAMQP_URL
  }

}