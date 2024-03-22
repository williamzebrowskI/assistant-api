provider "google" {
  project = local.ws_vars["project-id"]
  region  = local.ws_vars["region"]
}

terraform {
  backend "gcs" {
    bucket = "terraform-backend-bdt"
    prefix = "fafsa-chatgpt-assistant"
  }
}