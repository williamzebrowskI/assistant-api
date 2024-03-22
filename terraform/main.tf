resource "google_service_account" "emt_fafsagpt_sa" {
  account_id = "emt-fafsagpt-sa"
}
# IAM MEMBERS

# RASA Service Account (SA) Roles
resource "google_project_iam_member" "emt_fafsagpt_sa_required_roles" {
  for_each = toset([
    "cloudbuild.builds.editor",
    "run.admin",
    "container.developer",
    "logging.logWriter",
    "artifactregistry.admin",
    "secretmanager.secretAccessor",
    "secretmanager.viewer",
    "storage.admin",
    "iam.serviceAccountUser",
    "run.invoker",
  ])
  role    = "roles/${each.key}"
  project = local.ws_vars["project-id"]
  member  = "serviceAccount:${google_service_account.emt_fafsagpt_sa.email}"
}