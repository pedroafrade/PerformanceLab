"""Regression checks for the private-alpha infrastructure definition."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INFRA = ROOT / "infra" / "google-alpha"


def source(name: str) -> str:
    return (INFRA / name).read_text(encoding="utf-8")


def test_base_infrastructure_is_staged_before_application_deployment():
    variables = source("variables.tf")
    main = source("main.tf")

    assert 'variable "deploy_application"' in variables
    assert "default     = false" in variables
    assert "count = var.deploy_application ? 1 : 0" in main
    assert 'can(regex("@sha256:' in variables


def test_terraform_state_uses_protected_cloud_storage_backend():
    versions = source("versions.tf")

    assert 'backend "gcs"' in versions
    assert 'bucket = "performancelab-private-alpha-terraform-state"' in versions
    assert 'prefix = "terraform/alpha"' in versions


def test_alpha_uses_european_postgresql_with_recoverable_backups():
    variables = source("variables.tf")
    main = source("main.tf")

    assert 'default     = "europe-west1"' in variables
    assert 'startswith(var.region, "europe-")' in variables
    assert 'database_version = "POSTGRES_17"' in main
    assert "deletion_protection = true" in main
    assert "point_in_time_recovery_enabled = true" in main
    assert "retained_backups = 14" in main
    assert 'ipv4_enabled = true' in main
    assert "authorized_networks" not in main


def test_runtime_secrets_are_references_not_secret_values():
    main = source("main.tf")
    example = source("alpha.auto.tfvars.example")

    for setting in (
        "DATABASE_URL",
        "BETTER_STACK_ERROR_DSN",
        "GEMINI_API_KEY",
    ):
        assert setting in main
        assert setting not in example

    assert "google_secret_manager_secret_version" not in main
    assert 'mount_path = "/app/.streamlit"' in main
    assert 'path    = "secrets.toml"' in main


def test_application_has_small_bounded_runtime_and_separate_migrations():
    main = source("main.tf")

    assert "min_instance_count = 0" in main
    assert "max_instance_count = 2" in main
    assert 'memory = "1Gi"' in main
    assert 'resource "google_cloud_run_v2_job" "migrations"' in main
    assert 'command = ["alembic"]' in main
    assert 'args    = ["upgrade", "head"]' in main


def test_git_ignores_terraform_state_and_private_variables():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert ".terraform/" in ignore
    assert "*.tfstate" in ignore
    assert "*.tfvars" in ignore
    assert "!*.tfvars.example" in ignore
