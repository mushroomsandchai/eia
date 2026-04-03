variable "bucket_name" {
  type        = string
  description = "Bucket name to use as datalake. Blobs auto-exipre."
}

variable "dataset_name" {
  type        = string
  description = "Dataset name in the datawarehouse"
}

variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
}

variable "project_location" {
  type        = string
  description = "Google Cloud Project Location"
}
