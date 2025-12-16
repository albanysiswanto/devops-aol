variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
}

variable "region" {
  type        = string
  default     = "asia-southeast1"
  description = "Google Cloud region"
}

variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket"
}
