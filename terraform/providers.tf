provider "google" {
  project = local.ws_vars["project-id"]
  region  = local.ws_vars["region"]
}
terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = data.google_secret_manager_secret_version.api_token.secret_data
}

terraform {
  backend "gcs" {
    bucket = "terraform-backend-bdt"
    prefix = "fafsa-chatgpt-assistant"
  }
}