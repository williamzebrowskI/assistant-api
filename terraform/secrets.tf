# Access the secret version's value
data "google_secret_manager_secret_version" "bl_wildcard_crt" {
  secret  = "projects/${local.ws_vars["secret-id"]}/secrets/bl-wildcard-crt"
  version = "latest"
}

data "google_secret_manager_secret_version" "bl_wildcard_key" {
  secret  = "projects/${local.ws_vars["secret-id"]}/secrets/bl-wildcard-key"
  version = "latest"
}

data "google_secret_manager_secret_version" "api_token" {
  secret = "projects/${local.ws_vars["secret-id"]}/secrets/cloudflare_api_token"
  version = "latest"
}