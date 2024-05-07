# google_cloud_run_v2_service.openai_assistant
resource "google_cloud_run_v2_service" "openai_assistant" {
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"
  location = local.ws_vars["region"]
  name     = "openai-assistant"
  project  = local.ws_vars["project-id"]
  template {
    execution_environment            = "EXECUTION_ENVIRONMENT_GEN2"
    max_instance_request_concurrency = 80
    service_account                  = google_service_account.emt_fafsagpt_sa.email
    session_affinity                 = false
    timeout                          = "300s"

    containers {
      args    = []
      command = []
      image   = local.ws_vars["image"]
      env {
        name  = "ES_URL"
        value = local.ws_vars["es_url"]
      }
      env {
        name  = "ES_PORT"
        value = "443"
      }
      env {
        name  = "ES_INDEX"
        value = local.ws_vars["es_index"]
      }
      env {
        name  = "API_URI"
        value = local.ws_vars["api_uri"]
      }
      env {
        name  = "BASE_URL"
        value = local.ws_vars["base_url"]
      }
      env {
        name  = "CORS_ALLOWED_ORIGINS"
        value = local.ws_vars["cors"]
      }
      env {
        name = "OPENAI_API_KEY"

        value_source {
          secret_key_ref {
            secret  = "openai_api_key"
            version = "latest"
          }
        }
      }
      env {
        name = "ES_API_KEY"

        value_source {
          secret_key_ref {
            secret  = "es_api_key"
            version = "latest"
          }
        }
      }
      env {
        name = "FLASK_SECRET_KEY"

        value_source {
          secret_key_ref {
            secret  = "wyatt_ai_flask_secret_key"
            version = "latest"
          }
        }
      }
      env {
        name = "ASSISTANT_ID"

        value_source {
          secret_key_ref {
            secret  = "assistant_id"
            version = "latest"
          }
        }
      }
      ports {
        container_port = 8002
        name           = "http1"
      }

      resources {
        cpu_idle = false
        limits = {
          "cpu"    = "1000m"
          "memory" = "2G"
        }
        startup_cpu_boost = true
      }

      startup_probe {
        failure_threshold     = 5
        initial_delay_seconds = 60
        period_seconds        = 240
        timeout_seconds       = 240

        tcp_socket {
          port = 8002
        }
      }
    }

    scaling {
      max_instance_count = 8
      min_instance_count = 1
    }
    vpc_access {
      connector = local.ws_vars["vpc"]
      egress    = "ALL_TRAFFIC"
    }
  }

  timeouts {}

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }
}
