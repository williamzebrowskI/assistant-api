locals {
  env = {
    default = {
      region = "us-east4"
    }

    engplay = {
      project-id  = "bdt-eng-play"
      environment = "play"
      region      = "us-east4"
      repo        = "projects/bdt-eng-play/locations/us-east4/connections/BenefitsDataTrust/repositories/BenefitsDataTrust-fafsa-chatgpt-assistant"
      branch      = "^main$"
      image       = "us-east4-docker.pkg.dev/bdt-eng-play/docker/openai-assistant:latest"
      address     = "34.160.172.112"
      vpc         = "projects/bdt-eng-play/locations/us-east4/connectors/rasa-vpc-connect"
      secret-id   = "1044867322739"
      es_url      = "https://069e52dce53a40bfb5cfd26b233f29dd.us-east4.gcp.elastic-cloud.com"
      es_index    = "search-wyatt-ai"
    }

  }

  env_vars = contains(keys(local.env), terraform.workspace) ? terraform.workspace : "default"
  ws_vars  = merge(local.env["default"], local.env[local.env_vars])
}