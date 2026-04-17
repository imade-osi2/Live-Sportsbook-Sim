terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

resource "google_storage_bucket" "sportsbook_bucket" {
  name          = var.gcs_bucket_name
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_bigquery_dataset" "sportsbook_dataset" {
  dataset_id = var.bigquery_dataset
  location   = var.region
}