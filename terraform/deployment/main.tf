locals {
  port = 8080
}
resource "google_service_account" "dev_summit_a_service_account" {
  account_id   = "mcp-server-a-${terraform.workspace}"
  display_name = "MCP Server A Service Account in ${terraform.workspace}"
}

resource "google_cloud_run_v2_service" "dev_summit_backend" {
  provider            = google-beta
  name                = "dev-summit-backend-${terraform.workspace}"
  location            = var.my_region
  client              = "terraform"
  ingress             = "INGRESS_TRAFFIC_ALL"
  project             = var.my_project_id
  deletion_protection = false


  template {
    service_account = google_service_account.dev_summit_a_service_account.email

    containers {
      image = "${var.container_registry}/dev-summit:${terraform.workspace}"

      resources {
        startup_cpu_boost = true
        cpu_idle          = true

        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = local.port
        }
        period_seconds        = 60
        initial_delay_seconds = 120
      }

      startup_probe {
        http_get {
          path = "/health"
          port = local.port
        }
        period_seconds        = 5
        initial_delay_seconds = 30
      }
    }

    scaling {
      max_instance_count = 1
      min_instance_count = 0
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

resource "google_cloud_run_service_iam_binding" "mcp_server_a" {
  location = google_cloud_run_v2_service.dev_summit_backend.location
  project  = google_cloud_run_v2_service.dev_summit_backend.project
  service  = google_cloud_run_v2_service.dev_summit_backend.name
  role     = "roles/run.invoker"
  members = [
    "allUsers"
  ]
}