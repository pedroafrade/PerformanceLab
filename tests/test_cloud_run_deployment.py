"""
PerformanceLab

Google Cloud Run deployment configuration tests.
"""

from pathlib import (
    Path,
)


PROJECT_ROOT = (
    Path(__file__).parents[1]
)

DOCKERFILE_PATH = (
    PROJECT_ROOT
    / "Dockerfile"
)

DOCKERIGNORE_PATH = (
    PROJECT_ROOT
    / ".dockerignore"
)

DOCUMENTATION_PATH = (
    PROJECT_ROOT
    / "docs"
    / "GOOGLE_CLOUD_RUN.md"
)

APP_PATH = (
    PROJECT_ROOT
    / "app"
    / "app.py"
)

def dockerfile_text():

    return " ".join(
        DOCKERFILE_PATH.read_text(
            encoding="utf-8"
        ).split()
    )

def app_source_text():

    return " ".join(
        APP_PATH.read_text(
            encoding="utf-8"
        ).split()
    )

def dockerignore_entries():

    return {
        line.strip()
        for line in (
            DOCKERIGNORE_PATH
            .read_text(
                encoding="utf-8"
            )
            .splitlines()
        )
        if line.strip()
    }


def documentation_text():

    return " ".join(
        DOCUMENTATION_PATH.read_text(
            encoding="utf-8"
        ).split()
    )


def test_container_uses_supported_python():

    text = dockerfile_text()

    assert text.startswith(
        "FROM python:3.11-slim-bookworm"
    )


def test_container_installs_from_pyproject():

    text = dockerfile_text()

    assert (
        "COPY pyproject.toml README.md ./"
        in text
    )
    assert "python -m pip install ." in text
    assert "requirements.txt" not in text


def test_container_runs_without_root_privileges():

    text = dockerfile_text()

    assert "USER performancelab" in text
    assert "uid 10001" in text


def test_container_uses_cloud_run_port():

    text = dockerfile_text()

    assert "ENV PORT=8080" in text
    assert "EXPOSE 8080" in text
    assert "--server.address=0.0.0.0" in text
    assert "--server.port=${PORT:-8080}" in text
    assert "--server.headless=true" in text


def test_container_has_streamlit_health_check():

    text = dockerfile_text()

    assert "HEALTHCHECK" in text
    assert "/_stcore/health" in text


def test_docker_context_excludes_sensitive_content():

    entries = dockerignore_entries()

    required_entries = {
        ".git",
        ".env",
        ".env.*",
        ".streamlit/secrets.toml",
        "data",
        "backups",
        "exports",
        "*.pem",
        "*.key",
        "credentials*.json",
        "service-account*.json",
        "tests",
    }

    assert required_entries <= entries


def test_documentation_does_not_claim_deployment():

    text = documentation_text()

    assert (
        "CONFIGURAÇÃO PREPARADA — DEPLOYMENT PENDENTE"
        in text
    )
    assert (
        "A configuração no repositório não inicia custos"
        in text
    )
    assert (
        "Os convites permanecem bloqueados"
        in text
    )


def test_documentation_preserves_google_limits():

    text = documentation_text()

    assert "300 USD" in text
    assert "Dia 60" in text
    assert "Dia 85" in text
    assert "Dia 90" in text

def test_container_has_writable_home():

    text = dockerfile_text()

    assert (
        "ENV HOME=/home/performancelab"
        in text
    )
    assert (
        "--home /home/performancelab"
        in text
    )
    assert "/nonexistent" not in text


def test_container_can_use_environment_without_secrets_file():

    text = app_source_text()

    assert (
        "except StreamlitSecretNotFoundError"
        in text
    )
    assert "streamlit_secrets = {}" in text
    assert (
        "configuration_key in streamlit_secrets"
        in text
    )

def test_documentation_records_local_container_verification():

    text = documentation_text()

    assert (
        "imagem construída e testada localmente"
        in text
    )
    assert (
        "um email sem convite é recusado"
        in text
    )
    assert (
        "não constitui um deployment no Google Cloud"
        in text
    )
    assert (
        "não inicia o período experimental de 90 dias"
        in text
    )

def test_documentation_defines_secure_secret_delivery():

    text = documentation_text()

    assert "Google Secret Manager" in text
    assert (
        "/app/.streamlit/secrets.toml"
        in text
    )
    assert (
        "Variáveis de ambiente protegidas"
        in text
    )
    assert (
        ".streamlit/secrets.toml.example"
        in text
    )
    assert (
        "não inicia o período experimental de 90 dias"
        in text
    )

def test_secret_file_path_is_a_closed_code_block():

    source = DOCUMENTATION_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "```text\n"
        "/app/.streamlit/secrets.toml\n"
        "```"
        in source
    )
    assert (
        "### 4.3. Regras de segurança"
        in source
    )
    assert "- `DATABASE_URL` real;" in source

def test_documentation_records_automated_container_check():

    text = documentation_text()

    assert (
        "construção e verificação de saúde "
        "automáticas na CI"
        in text
    )
    assert (
        "confirma o endpoint "
        "`/_stcore/health`"
        in text
    )
    assert (
        "não é publicada num registo"
        in text
    )
    assert (
        "não é enviada para o Google Cloud"
        in text
    )

def test_documentation_explains_alpha_preflight():

    text = documentation_text()

    assert (
        "python scripts/"
        "check_alpha_configuration.py"
        in text
    )
    assert (
        "Alpha runtime configuration "
        "is structurally valid."
        in text
    )
    assert (
        "não deve imprimir passwords"
        in text
    )
    assert (
        "Esta verificação é apenas estrutural"
        in text
    )
    assert (
        "Uma falha deste comando bloqueia "
        "o arranque do ambiente alpha"
        in text
    )