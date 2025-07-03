# variables.tf
variable "project_id" {
  description = "The ID of your GCP project"
  type        = string
}

variable "region" {
  description = "The GCP region to deploy resources into"
  type        = string
  default     = "us-central1"
}

variable "gemini_api_key" {
  description = "The API key for Gemini or other LLM endpoint"
  type        = string
  sensitive   = true
}
