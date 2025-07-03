# main.tf
provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_project_service" "required_apis" {
  for_each = toset([
    "firestore.googleapis.com",
    "aiplatform.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudfunctions.googleapis.com",
    "storage.googleapis.com",
    "iam.googleapis.com"
  ])
  service = each.key
}

resource "google_service_account" "codessa_admin" {
  account_id   = "codessa-devos-admin"
  display_name = "Codessa DevOS Admin"
}

resource "google_project_iam_member" "datastore_access" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.codessa_admin.email}"
}

resource "google_project_iam_member" "vertex_ai_access" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.codessa_admin.email}"
}

resource "google_project_iam_member" "secret_access" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.codessa_admin.email}"
}

resource "google_service_account_key" "codessa_key" {
  service_account_id = google_service_account.codessa_admin.name
  keepers = {
    created_at = timestamp()
  }
}

resource "google_secret_manager_secret" "gemini_api_key" {
  secret_id = "gemini-api-key"
  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "gemini_key_version" {
  secret      = google_secret_manager_secret.gemini_api_key.id
  secret_data = var.gemini_api_key
}

resource "google_secret_manager_secret_iam_member" "allow_codessa_admin_to_read" {
  secret_id = google_secret_manager_secret.gemini_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.codessa_admin.email}"
}

output "service_account_email" {
  value = google_service_account.codessa_admin.email
}

output "private_key" {
  value     = google_service_account_key.codessa_key.private_key
  sensitive = true
}

output "public_key" {
  value = google_service_account_key.codessa_key.public_key
}
