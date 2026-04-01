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
  location      = var.project_location
  force_destroy = true

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 3
    }
  }
}

resource "google_bigquery_dataset" "dataset" {
  project                    = var.project_id
  dataset_id                 = var.dataset_name
  friendly_name              = "eia"
  location                   = var.project_location
  delete_contents_on_destroy = true
}