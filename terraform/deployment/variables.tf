variable "my_project_id" {
  description = "The project ID"
  default     = "braided-flow-434519-s1"
}

variable "my_region" {
  description = "The region the cluster in"
  default     = "europe-west3"
}

variable "container_registry" {
  description = "The container registry to host the application"
  default     = "europe-west3-docker.pkg.dev/braided-flow-434519-s1/my-coworker-docker-repo"
}