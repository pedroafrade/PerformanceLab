"""
PerformanceLab

Continuous integration workflow tests.
"""

from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
WORKFLOW_PATH = (
    PROJECT_ROOT
    / ".github"
    / "workflows"
    / "ci.yml"
)


def workflow_text() -> str:

    return WORKFLOW_PATH.read_text(
        encoding="utf-8",
    )


def test_ci_runs_for_main_and_pull_requests():

    text = workflow_text()

    assert "push:" in text
    assert "branches:" in text
    assert "- main" in text
    assert "pull_request:" in text


def test_ci_uses_supported_python_versions():

    text = workflow_text()

    assert '- "3.11"' in text
    assert '- "3.14"' in text
    assert "actions/setup-python@v5" in text


def test_ci_installs_from_pyproject():

    text = workflow_text()

    assert (
        'python -m pip install -e ".[test]"'
        in text
    )

    assert (
        "cache-dependency-path: pyproject.toml"
        in text
    )

    assert "requirements.txt" not in text


def test_ci_runs_static_check_and_full_pytest():

    text = workflow_text()

    assert (
        "python -m compileall -q "
        "app performancelab migrations"
        in text
    )

    assert "run: pytest -q" in text


def test_ci_uses_read_only_repository_permission():

    text = workflow_text()

    assert "permissions:" in text
    assert "contents: read" in text

def test_ci_builds_container_without_publishing():

    text = workflow_text()

    assert "container:" in text
    assert "name: Docker image" in text
    assert "docker build" in text
    assert (
        "--tag performancelab-alpha:ci"
        in text
    )
    assert (
        '--build-arg VCS_REF="${GITHUB_SHA}"'
        in text
    )
    assert "docker push" not in text
    assert "gcloud" not in text

def test_ci_verifies_container_health():

    text = workflow_text()

    assert (
        "--name performancelab-alpha-ci"
        in text
    )
    assert (
        "--env PERFORMANCELAB_ENV=local"
        in text
    )
    assert (
        "http://127.0.0.1:8080/"
        "_stcore/health"
        in text
    )
    assert "--retry-connrefused" in text
    assert "--retry-all-errors" in text
    assert "if: always()" in text
    assert (
        "docker rm --force "
        "performancelab-alpha-ci"
        in text
    )

def test_ci_rejects_incomplete_alpha_container():

    text = workflow_text()

    assert (
        "Reject incomplete alpha configuration"
        in text
    )
    assert (
        "--env PERFORMANCELAB_ENV=alpha"
        in text
    )
    assert (
        "Container unexpectedly accepted "
        "incomplete alpha configuration."
        in text
    )
    assert (
        "Alpha runtime configuration is "
        "incomplete or invalid."
        in text
    )
    assert "--fixed-strings" in text
    assert "--quiet" in text
    assert "alpha-preflight.log" in text

def test_ci_rejects_missing_alpha_authentication():

    text = workflow_text()

    assert (
        "SUPPORT_CONTACT_EMAIL="
        "support@example.invalid"
        in text
    )
    assert (
        "Reject missing alpha "
        "authentication configuration"
        in text
    )
    assert (
        "--env-file "
        '"${alpha_env}"'
        in text
    )
    assert (
        "Alpha authentication configuration "
        "is incomplete or invalid."
        in text
    )
    assert (
        "Container unexpectedly started "
        "without OIDC configuration."
        in text
    )
    assert "alpha-auth-preflight.log" in text

def test_ci_validates_mounted_authentication_example():

    text = workflow_text()

    assert (
        "Validate mounted authentication example"
        in text
    )
    assert (
        ".streamlit/secrets.toml.example"
        in text
    )
    assert (
        "target=/app/.streamlit/secrets.toml"
        in text
    )
    assert "readonly" in text
    assert "--entrypoint python" in text
    assert (
        "Alpha authentication configuration "
        "is structurally valid."
        in text
    )

def test_ci_rejects_unavailable_alpha_database():

    text = workflow_text()

    assert (
        "Reject unavailable alpha database"
        in text
    )
    assert "connect_timeout=3" in text
    assert (
        "Alpha database connection is unavailable."
        in text
    )
    assert (
        "Container unexpectedly started with "
        "an unavailable database."
        in text
    )
    assert "alpha-database-preflight.log" in text

def test_ci_verifies_container_image_revision():

    text = workflow_text()

    assert "Verify image revision" in text
    assert (
        "org.opencontainers.image.revision"
        in text
    )
    assert (
        'if [ "${revision}" != "${GITHUB_SHA}" ]'
        in text
    )
    assert (
        "Container image revision does not "
        "match the commit."
        in text
    )

def test_ci_verifies_non_root_container_execution():

    text = workflow_text()

    assert "Verify non-root execution" in text
    assert (
        "--format '{{ .Config.User }}'"
        in text
    )
    assert "--entrypoint id" in text
    assert (
        'if [ "${configured_user}" '
        '!= "performancelab" ]'
        in text
    )
    assert (
        'if [ "${runtime_uid}" != "10001" ]'
        in text
    )
    assert (
        "Container process does not use the "
        "expected non-root UID."
        in text
    )

def test_ci_verifies_image_excludes_sensitive_paths():

    text = workflow_text()

    assert (
        "Verify image excludes sensitive paths"
        in text
    )
    assert "--entrypoint sh" in text

    forbidden_paths = (
        "/app/.env",
        "/app/.git",
        "/app/.streamlit/secrets.toml",
        "/app/data",
        "/app/backups",
        "/app/exports",
    )

    for forbidden_path in forbidden_paths:

        assert forbidden_path in text

    assert (
        'if [ -e "${forbidden_path}" ]'
        in text
    )
    assert (
        "Sensitive path found in container image"
        in text
    )

def test_ci_verifies_image_excludes_alpha_configuration():

    text = workflow_text()

    assert (
        "Verify image excludes alpha configuration"
        in text
    )
    assert (
        "--format "
        "'{{ range .Config.Env }}"
        "{{ println . }}"
        "{{ end }}'"
        in text
    )

    forbidden_names = (
        "PERFORMANCELAB_ENV",
        "DATABASE_URL",
        "PRIVACY_CONTACT_EMAIL",
        "SUPPORT_CONTACT_EMAIL",
        "GEMINI_API_KEY",
        "BETTER_STACK_ERROR_DSN",
    )

    for forbidden_name in forbidden_names:

        assert forbidden_name in text

    assert (
        '"^${forbidden_name}="'
        in text
    )
    assert (
        "Alpha configuration found in "
        "container image"
        in text
    )

def test_ci_verifies_application_code_is_read_only():

    text = workflow_text()

    assert (
        "Verify application code is read-only"
        in text
    )

    protected_paths = (
        "/app/app/app.py",
        "/app/scripts/check_alpha_configuration.py",
        "/app/scripts/check_alpha_auth_configuration.py",
        "/app/scripts/check_alpha_database.py",
        "/app/scripts/check_alpha_migrations.py",
    )

    for protected_path in protected_paths:

        assert protected_path in text

    assert (
        'if [ -w "${protected_path}" ]'
        in text
    )
    assert (
        "Application code is writable by "
        "the runtime user"
        in text
    )

