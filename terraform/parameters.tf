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
      es_url      = "069e52dce53a40bfb5cfd26b233f29dd.us-east4.gcp.elastic-cloud.com"
      es_index    = "search-wyatt-ai"
      api_uri     = "wyatt-openai-play.bdtrust.org"
      subdomain   = "wyatt-openai-play"
      zone_id     = "e97957d24b2e45b7b42884d8cc64e9b4"
      base_url    = "fafsa-nonprod.bdtrust.org"
      approval    = "false"
      cors        = "http://127.0.0.1:5500, http://localhost:8000, http://localhost:3000, http://localhost:8002, https://benefitsdatatrust.github.io, http://127.0.0.1:8002"
    }

    chatstage = {
      project-id  = "bdt-chatbot-stage"
      environment = "stage"
      region      = "us-east4"
      repo        = "projects/bdt-chatbot-stage/locations/us-east4/connections/Github/repositories/BenefitsDataTrust-fafsa-chatgpt-assistant"
      branch      = "^main$"
      image       = "us-east4-docker.pkg.dev/bdt-chatbot-stage/docker/openai-assistant:latest"
      address     = "35.190.64.230"
      vpc         = "projects/bdt-chatbot-stage/locations/us-east4/connectors/cloud-run-vpc-connector"
      secret-id   = "900223827522"
      es_url      = "72d56f45ab6c42aabcf5cf7d00790870.us-east4.gcp.elastic-cloud.com"
      es_index    = "search-wyatt-ai"
      api_uri     = "wyatt-openai-stage.bdtrust.org"
      subdomain   = "wyatt-openai-stage"
      zone_id     = "e97957d24b2e45b7b42884d8cc64e9b4"
      approval    = "true"
      base_url    = "fafsa-nonprod.bdtrust.org"
      cors        = "https://develop.getfafsahelp.org, https://deploy-preview-327--awesome-varahamihira-483edb.netlify.app, https://deploy-preview-345--awesome-varahamihira-483edb.netlify.app, https://preview-build-northstar--getfafsahelp.netlify.app/"

    }

    chatprod = {
      project-id  = "bdt-chatbot-prod"
      environment = "prod"
      region      = "us-east4"
      repo        = "projects/bdt-chatbot-prod/locations/us-east4/connections/Github/repositories/BenefitsDataTrust-fafsa-chatgpt-assistant"
      branch      = "^main$"
      image       = "us-east4-docker.pkg.dev/bdt-chatbot-prod/docker/openai-assistant:latest"
      address     = "34.111.16.227"
      vpc         = "projects/bdt-chatbot-prod/locations/us-east4/connectors/cloud-run-vpc-connector"
      secret-id   = "814123834976"
      es_url      = "1d87119333f04525afd6c68643317e9c.us-east4.gcp.elastic-cloud.com"
      es_index    = "search-wyatt-ai"
      api_uri     = "wyatt-openai.bdtrust.org"
      subdomain   = "wyatt-openai"
      zone_id     = "e97957d24b2e45b7b42884d8cc64e9b4"
      approval    = "true"
      base_url    = "fafsa-nonprod.bdtrust.org"
      cors        = "https://getfafsahelp.org"
    }

  }

  env_vars = contains(keys(local.env), terraform.workspace) ? terraform.workspace : "default"
  ws_vars  = merge(local.env["default"], local.env[local.env_vars])
}