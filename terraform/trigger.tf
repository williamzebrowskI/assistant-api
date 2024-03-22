resource "google_cloudbuild_trigger" "openai_assistant_trigger" {
  name            = "openai-assistant"
  description     = "builds the latest image for open ai assistant"
  service_account = google_service_account.emt_fafsagpt_sa.id
  disabled        = false
  filename        = "cloudbuild.yaml"
  included_files = [
    "*.py",
    "index.html",
    "requirements.txt",
    "cloudbuild.yaml",
    "Dockerfile",
  ]
  location = local.ws_vars["region"]
  project  = local.ws_vars["project-id"]

  substitutions = {

  }
  tags = [

  ]
  approval_config {
    approval_required = true
  }

  repository_event_config {
    repository = local.ws_vars["repo"]

    push {
      branch       = local.ws_vars["branch"]
      invert_regex = false
    }
  }
}
