variable "project_id" {
  type    = string
  default = "de26-live-sportsbook-sim"
}

variable "region" {
  type    = string
  default = "US"
}

variable "gcs_bucket_name" {
  type    = string
  default = "de26-live-sportsbook-bucket"
}

variable "bigquery_dataset" {
  type    = string
  default = "de26_sportsbook_analytics"
}