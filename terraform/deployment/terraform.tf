# https://www.terraform.io/language/settings/backends/gcs
terraform {
  backend "gcs" {
    bucket = "tf-state-23a266d7"
    prefix = "terraform/state/dev-summit"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.34.0"
    }
  }
}