variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "firestore_location" {
  description = "Firestore database location"
  type        = string
  default     = "nam5"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "function_runtime" {
  description = "Cloud Functions runtime"
  type        = string
  default     = "python311"
}

variable "function_memory" {
  description = "Memory allocation for Cloud Functions"
  type        = string
  default     = "512Mi"
}

variable "function_timeout" {
  description = "Timeout for Cloud Functions in seconds"
  type        = number
  default     = 300
}

variable "function_max_instances" {
  description = "Maximum number of function instances"
  type        = number
  default     = 10
}

variable "function_min_instances" {
  description = "Minimum number of function instances"
  type        = number
  default     = 0
}

variable "acreditta_api_url" {
  description = "Acreditta API base URL"
  type        = string
  default     = "https://api.acreditta.com/v1"
}

variable "sis_db_host" {
  description = "SIS database host"
  type        = string
  default     = ""
}

variable "sis_db_name" {
  description = "SIS database name"
  type        = string
  default     = "sis_production"
}
