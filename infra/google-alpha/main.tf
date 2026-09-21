locals {
  service_name = "performancelab-alpha"

  required_services = toset([
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "secretmanager.googleapis.com",
    "sqladmin.googleapis.com",
  ])

  secret_ids = toset([
    "performancelab-alpha-better-stack-dsn",
    "performancelab-alpha-database-url",
    "performancelab-alpha-gemini-api-key",
    "performancelab-alpha-oidc-toml",
  ])

  runtime_environment = {
    PERFORMANCELAB_ENV                  = "alpha"
    PRIVACY_CONTACT_EMAIL               = var.privacy_contact_email
    SUPPORT_CONTACT_EMAIL               = var.support_contact_email
    TRAINING_COACH_ENABLED              = tostring(var.training_coach_enabled)
    TRAINING_COACH_USER_DAILY_LIMIT     = "5"
    TRAINING_COACH_GLOBAL_DAILY_LIMIT   = "25"
    RETENTION_INACTIVE_ACCOUNT_DAYS     = "90"
    RETENTION_INACTIVITY_NOTICE_DAYS    = "14"
    RETENTION_TRAINING_COACH_USAGE_DAYS = "30"
    RETENTION_CONSENT_EVIDENCE_DAYS     = "0"
    RETENTION_UNUSED_INVITATION_DAYS    = "14"
    RETENTION_EXPIRED_INVITATION_DAYS   = "7"
    RETENTION_APPLICATION_LOG_DAYS      = "14"
    RETENTION_ERROR_ALERT_DAYS          = "30"
    RETENTION_BACKUP_DAYS               = "14"
    RETENTION_SUPPORT_REQUEST_DAYS      = "90"
    RETENTION_POST_ALPHA_DAYS           = "30"
  }
}

resource "google_project_service" "required" {
  for_each = local.required_services

  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "application" {
  location      = var.region
  repository_id = "performancelab"
  description   = "Versioned images for the PerformanceLab private alpha"
  format        = "DOCKER"

  depends_on = [google_project_service.required]
}

resource "google_service_account" "application" {
  account_id   = "performancelab-alpha"
  display_name = "PerformanceLab private alpha"
}

resource "google_project_iam_member" "cloud_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.application.email}"
}

resource "google_secret_manager_secret" "runtime" {
  for_each = local.secret_ids

  secret_id = each.value
  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }

  depends_on = [google_project_service.required]
}

resource "google_secret_manager_secret_iam_member" "application" {
  for_each = google_secret_manager_secret.runtime

  secret_id = each.value.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.application.email}"
}

resource "google_sql_database_instance" "alpha" {
  name             = "performancelab-alpha"
  database_version = "POSTGRES_17"
  region           = var.region

  deletion_protection = true

  settings {
    tier              = var.database_tier
    # PostgreSQL 16+ defaults to Enterprise Plus unless the edition is
    # explicit. Shared-core tiers such as db-f1-micro require Enterprise.
    edition           = "ENTERPRISE"
    availability_type = "ZONAL"
    disk_type         = "PD_SSD"
    disk_size         = 10
    disk_autoresize   = true

    ip_configuration {
      # No network is authorised directly. Cloud Run connects through the
      # managed Cloud SQL connector, which validates IAM and encrypts traffic.
      ipv4_enabled = true
    }

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = "eu"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7

      backup_retention_settings {
        retained_backups = 14
        retention_unit   = "COUNT"
      }
    }

    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }
  }

  depends_on = [google_project_service.required]
}

resource "google_sql_database" "application" {
  name     = "performancelab"
  instance = google_sql_database_instance.alpha.name
}

resource "google_cloud_run_v2_service" "application" {
  count = var.deploy_application ? 1 : 0

  name                = local.service_name
  location            = var.region
  deletion_protection = true
  ingress             = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.application.email
    timeout         = "300s"

    scaling {
      min_instance_count = 0
      max_instance_count = 2
    }

    containers {
      image = var.container_image

      ports {
        container_port = 8080
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "1Gi"
        }
        cpu_idle = true
      }

      dynamic "env" {
        for_each = local.runtime_environment
        content {
          name  = env.key
          value = env.value
        }
      }

      env {
        name = "DATABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.runtime["performancelab-alpha-database-url"].secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "BETTER_STACK_ERROR_DSN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.runtime["performancelab-alpha-better-stack-dsn"].secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GEMINI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.runtime["performancelab-alpha-gemini-api-key"].secret_id
            version = "latest"
          }
        }
      }

      volume_mounts {
        name       = "cloudsql"
        mount_path = "/cloudsql"
      }

      volume_mounts {
        name       = "oidc"
        mount_path = "/app/.streamlit"
      }

      startup_probe {
        initial_delay_seconds = 5
        timeout_seconds       = 5
        period_seconds        = 5
        failure_threshold     = 24

        http_get {
          path = "/_stcore/health"
          port = 8080
        }
      }
    }

    volumes {
      name = "cloudsql"
      cloud_sql_instance {
        instances = [google_sql_database_instance.alpha.connection_name]
      }
    }

    volumes {
      name = "oidc"
      secret {
        secret = google_secret_manager_secret.runtime["performancelab-alpha-oidc-toml"].secret_id
        items {
          version = "latest"
          path    = "secrets.toml"
          mode    = 292
        }
      }
    }
  }

  depends_on = [
    google_project_iam_member.cloud_sql_client,
    google_secret_manager_secret_iam_member.application,
  ]
}

# The address is reachable so Streamlit can complete OIDC in a normal browser.
# PerformanceLab still refuses every identity without an individual invitation.
resource "google_cloud_run_v2_service_iam_member" "browser_access" {
  count = var.deploy_application ? 1 : 0

  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.application[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_v2_job" "migrations" {
  count = var.deploy_application ? 1 : 0

  name                = "performancelab-alpha-migrations"
  location            = var.region
  deletion_protection = true

  template {
    template {
      service_account = google_service_account.application.email
      timeout         = "600s"
      max_retries     = 0

      containers {
        image   = var.container_image
        command = ["alembic"]
        args    = ["upgrade", "head"]

        env {
          name  = "PERFORMANCELAB_ENV"
          value = "alpha"
        }

        env {
          name = "DATABASE_URL"
          value_source {
            secret_key_ref {
              secret  = google_secret_manager_secret.runtime["performancelab-alpha-database-url"].secret_id
              version = "latest"
            }
          }
        }

        volume_mounts {
          name       = "cloudsql"
          mount_path = "/cloudsql"
        }
      }

      volumes {
        name = "cloudsql"
        cloud_sql_instance {
          instances = [google_sql_database_instance.alpha.connection_name]
        }
      }
    }
  }

  depends_on = [
    google_project_iam_member.cloud_sql_client,
    google_secret_manager_secret_iam_member.application,
  ]
}
