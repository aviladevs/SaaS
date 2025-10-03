# Ávila DevOps SaaS - Infrastructure as Code
# Arquivo principal do Terraform para provisionamento da infraestrutura

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
  backend "gcs" {
    bucket = "aviladevops-terraform-state"
    prefix = "saas-platform"
  }
}

# Variáveis
variable "project_id" {
  description = "ID do projeto GCP"
  type        = string
}

variable "region" {
  description = "Região GCP"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Ambiente (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Rede VPC
resource "google_compute_network" "saas_vpc" {
  name                    = "aviladevops-saas-vpc-${var.environment}"
  auto_create_subnetworks = false
}

# Sub-rede privada
resource "google_compute_subnetwork" "private_subnet" {
  name          = "aviladevops-private-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  network       = google_compute_network.saas_vpc.id
  region        = var.region

  private_ip_google_access = true
}

# Cloud Router para NAT
resource "google_compute_router" "router" {
  name    = "aviladevops-router-${var.environment}"
  network = google_compute_network.saas_vpc.name
  region  = var.region
}

resource "google_compute_router_nat" "nat" {
  name                               = "aviladevops-nat-${var.environment}"
  router                             = google_compute_router.router.name
  region                             = var.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "postgres" {
  name             = "aviladevops-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region

  settings {
    tier = var.environment == "prod" ? "db-f1-micro" : "db-f1-micro"
    disk_size = 10

    backup_configuration {
      enabled = true
      window  = "02:00-06:00"
    }

    maintenance_window {
      day  = 1
      hour = 3
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.saas_vpc.id
    }
  }

  deletion_protection = var.environment == "prod"
}

# Banco de dados principal
resource "google_sql_database" "saas_db" {
  name     = "aviladevops_saas"
  instance = google_sql_database_instance.postgres.name
}

# Usuário do banco
resource "google_sql_user" "saas_user" {
  name     = "saas_user"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
}

# Cloud Memorystore (Redis)
resource "google_redis_instance" "redis" {
  name           = "aviladevops-redis-${var.environment}"
  memory_size_gb = var.environment == "prod" ? 5 : 1
  region         = var.region

  authorized_network = google_compute_network.saas_vpc.id

  redis_version = "REDIS_7_0"
}

# Cloud Run services
resource "google_cloud_run_service" "landing_page" {
  name     = "landing-page-service-${var.environment}"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/${var.project_id}/landing-page-service:latest"

        ports {
          container_port = 8000
        }

        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1000m"
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DATABASE_URL"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_url.secret_id
              key  = "latest"
            }
          }
        }
      }

      service_account_name = google_service_account.saas_runner.email
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# Load Balancer
resource "google_compute_global_address" "lb_ip" {
  name = "aviladevops-lb-ip-${var.environment}"
}

resource "google_compute_url_map" "url_map" {
  name            = "aviladevops-url-map-${var.environment}"
  default_service = google_compute_backend_service.landing_page_backend.id
}

resource "google_compute_backend_service" "landing_page_backend" {
  name                  = "landing-page-backend-${var.environment}"
  protocol              = "HTTP"
  timeout_sec           = 30
  load_balancing_scheme = "EXTERNAL"

  backend {
    group = google_compute_region_network_endpoint_group.landing_page_neg.id
  }

  health_checks = [google_compute_health_check.landing_page_health.id]
}

resource "google_compute_region_network_endpoint_group" "landing_page_neg" {
  name                  = "landing-page-neg-${var.environment}"
  region                = var.region
  network_endpoint_type = "SERVERLESS"
  cloud_run {
    service = google_cloud_run_service.landing_page.name
  }
}

resource "google_compute_health_check" "landing_page_health" {
  name = "landing-page-health-${var.environment}"

  http_health_check {
    port = 8000
    request_path = "/health/"
  }

  check_interval_sec  = 30
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 3
}

# Cloud Storage bucket
resource "google_storage_bucket" "static_assets" {
  name     = "aviladevops-static-${var.project_id}-${var.environment}"
  location = "US"

  uniform_bucket_level_access = true

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Secret Manager
resource "google_secret_manager_secret" "db_url" {
  secret_id = "db-url-${var.environment}"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_url_version" {
  secret = google_secret_manager_secret.db_url.id

  secret_data = "postgresql://${google_sql_user.saas_user.name}:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.saas_db.name}"
}

# Service Account
resource "google_service_account" "saas_runner" {
  account_id   = "saas-runner-${var.environment}"
  display_name = "SaaS Runner Service Account"
}

resource "google_project_iam_member" "saas_runner_roles" {
  for_each = toset([
    "roles/cloudtranslate.user",
    "roles/secretmanager.secretAccessor",
    "roles/storage.objectViewer",
    "roles/storage.objectCreator",
  ])

  role   = each.key
  member = "serviceAccount:${google_service_account.saas_runner.email}"
}

# Firewall rules
resource "google_compute_firewall" "allow_health_checks" {
  name    = "allow-health-checks-${var.environment}"
  network = google_compute_network.saas_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["8000"]
  }

  source_ranges = ["130.211.0.0/22", "35.191.0.0/16"]
}

# Outputs
output "database_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}

output "load_balancer_ip" {
  value = google_compute_global_address.lb_ip.address
}

output "cloud_run_url" {
  value = google_cloud_run_service.landing_page.status[0].url
}

output "storage_bucket" {
  value = google_storage_bucket.static_assets.name
}

# Random password generation
resource "random_password" "db_password" {
  length  = 32
  special = true
}
