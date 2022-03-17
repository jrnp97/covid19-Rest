# Template to define module output values

output "api_server_url" {
  value = heroku_app.api_app.web_url
}
