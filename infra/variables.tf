variable "resource_group_name" {
  type    = string
  default = "happymeter"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "environment_name" {
  type    = string
  default = "happymeter"
}

variable "law_name" {
  type    = string
  default = "happymeter"
}

variable "acr_name" {
  type    = string
  default = "happyregistry"
}

variable "backend_name" {
  type    = string
  default = "happymeter-backend"
}

variable "frontend_name" {
  type    = string
  default = "happymeter-frontend"
}

variable "container_app_environment_name" {
  type    = string
  default = "happymeter"
}

variable "storage_env_name" {
  type    = string
  default = "duckdb-storage"
}

variable "storage_account_name" {
  type        = string
  default     = "happymeterdb"
  description = "Base storage account name"
}

variable "storage_share_name" {
  type    = string
  default = "duckdb-data"
}

variable "tag" {
  type    = string
  default = "1"
}
