terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.25.0"
    }
  }
}

provider "google" {
  # Configuration options
}

resource "google_storage_bucket" "no-age-enabled" {
  provider      = google-beta
  project       = var.project_id
  name          = var.bucket_name
  location      = "US"
  force_destroy = true
}

resource "google_bigquery_dataset" "dataset" {
  project                     = var.project_id
  dataset_id                  = var.dataset_name
  friendly_name               = "eia"
  location                    = "US"
  default_table_expiration_ms = 3600000
}