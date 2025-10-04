# Ávila DevOps SaaS - Infrastructure Improvements (Terraform)
# Melhorias adicionais para produção baseadas no feedback

# =============================================================================
# VARIÁVEIS MELHORADAS
# =============================================================================

variable "enable_monitoring" {
  description = "Habilitar monitoramento avançado"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Dias de retenção de backup"
  type        = number
  default     = 30
}

# =============================================================================
# MELHORIAS DE MONITORAMENTO
# =============================================================================

# Uptime checks para todos os serviços
resource "google_monitoring_uptime_check_config" "service_checks" {
  for_each = var.environment == "prod" ? {
    landing-page = "https://aviladevops.com.br/health/"
    sistema      = "https://sistema.aviladevops.com.br/health/"
    fiscal       = "https://fiscal.aviladevops.com.br/health/"
    clinica      = "https://clinica.aviladevops.com.br/health/"
    admin        = "https://admin.aviladevops.com.br/health/"
  } : {}

  display_name = "saas-${each.key}-uptime-${var.environment}"
  timeout      = "10s"

  http_check {
    path     = "/health/"
    port     = "443"
    use_ssl  = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = split("://", each.value)[1]
    }
  }

  period = "60s"
}

# Alert policies para métricas críticas
resource "google_monitoring_alert_policy" "high_error_rate" {
  count = var.environment == "prod" ? 1 : 0

  display_name = "High Error Rate - SaaS ${var.environment}"
  combiner     = "OR"

  conditions {
    display_name = "Error rate > 5%"

    condition_threshold {
      filter          = "metric.type=\"run.googleapis.com/request_count\" resource.type=\"cloud_run_revision\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "300s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.slack.id]
}

# =============================================================================
# MELHORIAS DE BACKUP
# =============================================================================

# Backup automático melhorado
resource "google_sql_database_instance" "postgres" {
  # ... existing code ...

  settings {
    # ... existing code ...

    backup_configuration {
      enabled                        = true
      window                         = "02:00-06:00"
      point_in_time_recovery_enabled = var.environment == "prod"
      transaction_log_retention_days = var.backup_retention_days
    }
  }
}

# Cloud Storage para backups
resource "google_storage_bucket" "backups" {
  count = var.environment == "prod" ? 1 : 0

  name     = "aviladevops-backups-${var.project_id}"
  location = "US"

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = var.backup_retention_days
    }
    action {
      type = "Delete"
    }
  }

  versioning {
    enabled = true
  }
}

# =============================================================================
# MELHORIAS DE SEGURANÇA
# =============================================================================

# Cloud Armor melhorado
resource "google_compute_security_policy" "cloud_armor" {
  name = "aviladevops-cloud-armor-${var.environment}"

  # Regra padrão - permitir
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }

  # Proteção contra XSS
  rule {
    action   = "deny(403)"
    priority = "1000"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "XSS protection"
  }

  # Proteção contra SQL injection
  rule {
    action   = "deny(403)"
    priority = "900"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "SQL injection protection"
  }

  # Rate limiting por IP
  rule {
    action   = "throttle"
    priority = "800"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"

      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 100
        interval_sec = 60
      }
    }

    description = "Rate limiting per IP"
  }
}

# =============================================================================
# MELHORIAS DE PERFORMANCE
# =============================================================================

# CDN para arquivos estáticos
resource "google_compute_backend_bucket" "static_cdn" {
  count = var.environment == "prod" ? 1 : 0

  name        = "aviladevops-static-cdn"
  bucket_name = google_storage_bucket.static_assets.name
  enable_cdn  = true

  cdn_policy {
    cache_mode = "CACHE_ALL_STATIC"
    default_ttl = 3600
    max_ttl     = 86400

    cache_key_policy {
      include_host           = true
      include_protocol       = true
      include_query_string   = false
    }
  }
}

# Memorystore Redis com configurações otimizadas
resource "google_redis_instance" "redis" {
  # ... existing code ...

  memory_size_gb = var.environment == "prod" ? 10 : 2

  redis_configs = {
    "maxmemory-policy" = "allkeys-lru"
    "notify-keyspace-events" = "Ex"
  }

  maintenance_policy {
    weekly_maintenance_window {
      day = "SUNDAY"
      start_time {
        hours = 2
        minutes = 0
      }
    }
  }
}

# =============================================================================
# MELHORIAS DE ESCALABILIDADE
# =============================================================================

# Cloud Run com auto-scaling melhorado
resource "google_cloud_run_service" "main_services" {
  for_each = {
    landing-page = { memory = "512Mi", cpu = "1000m" }
    sistema      = { memory = "1Gi", cpu = "2000m" }
    fiscal       = { memory = "1Gi", cpu = "2000m" }
    clinica      = { memory = "512Mi", cpu = "1000m" }
    admin        = { memory = "1Gi", cpu = "2000m" }
  }

  name     = "${each.key}-service-${var.environment}"
  location = var.region

  template {
    spec {
      container_concurrency = 80
      timeout_seconds      = 300

      containers {
        image = "gcr.io/${var.project_id}/${each.key}-service:latest"

        resources {
          limits = {
            memory = each.value.memory
            cpu    = each.value.cpu
          }
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
      }

      # Auto-scaling baseado em métricas
      max_instance_request_concurrency = 1000
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# =============================================================================
# MELHORIAS DE LOGGING
# =============================================================================

# Cloud Logging sinks para análise externa
resource "google_logging_project_sink" "bigquery_sink" {
  count = var.environment == "prod" ? 1 : 0

  name        = "saas-logs-to-bigquery"
  destination = "bigquery.googleapis.com/projects/${var.project_id}/datasets/saas_logs"

  filter = "resource.type=cloud_run_revision"

  unique_writer_identity = true
}

# Dataset BigQuery para análise de logs
resource "google_bigquery_dataset" "logs_dataset" {
  count = var.environment == "prod" ? 1 : 0

  dataset_id = "saas_logs"
  location   = "US"

  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }

  access {
    role   = "READER"
    domain = "aviladevops.com.br"
  }
}

# =============================================================================
# MELHORIAS DE NOTIFICAÇÕES
# =============================================================================

# Canal Slack para notificações
resource "google_monitoring_notification_channel" "slack" {
  display_name = "Slack Notifications"
  type         = "slack"

  labels = {
    channel_name = "#alerts"
    auth_token   = var.slack_token
  }
}

# Canal Email para notificações críticas
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notifications"
  type         = "email"

  labels = {
    email_address = "alerts@aviladevops.com.br"
  }
}

# =============================================================================
# MELHORIAS DE CUSTO
# =============================================================================

# Budget para monitoramento de gastos
resource "google_billing_budget" "monthly_budget" {
  count = var.environment == "prod" ? 1 : 0

  billing_account = var.billing_account_id
  display_name    = "SaaS Monthly Budget"

  budget_filter {
    projects = ["projects/${var.project_id}"]
  }

  amount {
    specified_amount {
      currency_code = "BRL"
      units         = "1000"  # R$ 1000 por mês
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "CURRENT_SPEND"
  }

  all_updates_rule {
    monitoring_notification_channels = [
      google_monitoring_notification_channel.slack.id,
      google_monitoring_notification_channel.email.id
    ]
  }
}

# =============================================================================
# OUTPUTS MELHORADOS
# =============================================================================

output "monitoring_urls" {
  description = "URLs para monitoramento"
  value = var.environment == "prod" ? {
    uptime_checks = "https://console.cloud.google.com/monitoring/uptime"
    grafana       = "https://grafana.aviladevops.com.br"
    sentry        = "https://sentry.aviladevops.com.br"
  } : {}
}

output "backup_bucket" {
  description = "Bucket para backups"
  value       = var.environment == "prod" ? google_storage_bucket.backups[0].name : null
}

output "cdn_url" {
  description = "URL do CDN para arquivos estáticos"
  value       = var.environment == "prod" ? "https://cdn.aviladevops.com.br" : null
}
