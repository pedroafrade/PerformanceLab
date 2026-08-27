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
        "logs",
        "*.backup",
        "*.dump",
        "*.bak",
        "*_backup.sql",
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

def test_alpha_preflight_documentation_has_closed_code_blocks():

    source = DOCUMENTATION_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "```powershell\n"
        "python scripts/check_alpha_configuration.py\n"
        "```"
        in source
    )
    assert (
        "```text\n"
        "Alpha runtime configuration is structurally valid.\n"
        "```"
        in source
    )
    assert "- ambiente definido como `alpha`;" in source
    assert "- ligação real ao PostgreSQL;" in source

def test_container_includes_alpha_configuration_preflight():

    text = dockerfile_text()

    assert (
        "COPY scripts/check_alpha_configuration.py "
        "./scripts/check_alpha_configuration.py"
        in text
    )
def test_alpha_container_runs_preflight_before_streamlit():

    text = dockerfile_text()

    assert (
        'if [ \\"${PERFORMANCELAB_ENV:-local}\\" '
        '= \\"alpha\\" ]'
        in text
    )
    assert (
        "python scripts/"
        "check_alpha_configuration.py || exit 1"
        in text
    )
    assert (
        "exec python -m streamlit run app/app.py"
        in text
    )

def test_documentation_records_automatic_alpha_gate():

    text = documentation_text()

    assert (
        "Bloqueio automático do arranque alpha"
        in text
    )
    assert (
        "o Streamlit não é iniciado"
        in text
    )
    assert (
        "preflight alpha integrado e recusa "
        "automática validada na CI"
        in text
    )
    assert (
        "Não contém segredos reais"
        in text
    )
    assert (
        "não testa a ligação ao Cloud SQL"
        in text
    )

def test_container_includes_authentication_preflight():

    text = dockerfile_text()

    assert (
        "COPY scripts/"
        "check_alpha_auth_configuration.py "
        "./scripts/"
        "check_alpha_auth_configuration.py"
        in text
    )

def test_container_prepares_authentication_mount_point():

    text = dockerfile_text()

    assert (
        "mkdir -p /app/.streamlit"
        in text
    )
    assert (
        "chown -R "
        "performancelab:performancelab /app"
        in text
    )

def test_documentation_records_oidc_preflight():

    text = documentation_text()

    assert (
        "Verificação da configuração OIDC"
        in text
    )
    assert (
        "/app/.streamlit/secrets.toml"
        in text
    )
    assert (
        "configuração OIDC estruturalmente "
        "validada antes do arranque"
        in text
    )
    assert (
        "o contentor termina antes de "
        "iniciar o Streamlit"
        in text
    )
    assert (
        "não confirma que as credenciais "
        "Google são reais"
        in text
    )

def test_oidc_documentation_is_not_duplicated():

    source = DOCUMENTATION_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        source.count(
            "### 8.3. Verificação "
            "da configuração OIDC"
        )
        == 1
    )
    assert (
        "```text\n"
        "/app/.streamlit/secrets.toml\n"
        "```"
        in source
    )

def test_container_includes_database_preflight():

    text = dockerfile_text()

    assert (
        "COPY scripts/check_alpha_database.py "
        "./scripts/check_alpha_database.py"
        in text
    )

def test_container_includes_migration_preflight():

    text = dockerfile_text()

    assert (
        "COPY scripts/check_alpha_migrations.py "
        "./scripts/check_alpha_migrations.py"
        in text
    )

def test_alpha_runs_all_preflights_before_streamlit():

    text = dockerfile_text()

    expected_sequence = (
        "python scripts/"
        "check_alpha_configuration.py || exit 1; "
        "python scripts/"
        "check_alpha_auth_configuration.py || exit 1; "
        "python scripts/"
        "check_alpha_database.py || exit 1; "
        "python scripts/"
        "check_alpha_migrations.py || exit 1; "
        "fi; exec python -m streamlit"
    )

    assert expected_sequence in text

def test_documentation_records_database_preflight():

    text = documentation_text()

    assert (
        "Verificação da ligação PostgreSQL"
        in text
    )
    assert (
        "executa a verificação de saúde "
        "existente com `SELECT 1`"
        in text
    )
    assert (
        "Alpha database connection "
        "is unavailable."
        in text
    )
    assert (
        "não apresenta o `DATABASE_URL`"
        in text
    )
    assert (
        "ligação PostgreSQL obrigatória "
        "antes do arranque alpha"
        in text
    )
    assert (
        "não valida ainda uma ligação "
        "real ao Google Cloud SQL"
        in text
    )

def test_documentation_preserves_pending_cloud_run_service():

    source = DOCUMENTATION_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "- [ ] serviço Cloud Run criado;"
        in source
    )
    assert (
        "- [x] ligação PostgreSQL obrigatória "
        "antes do arranque alpha;"
        in source
    )
    assert (
        source.index(
            "- [x] ligação PostgreSQL obrigatória "
            "antes do arranque alpha;"
        )
        < source.index(
            "- [ ] serviço Cloud Run criado;"
        )
    )

def test_documentation_records_migration_preflight():

    text = documentation_text()

    assert "Verificação das migrações" in text
    assert (
        "quarto preflight é executado depois "
        "da verificação da ligação PostgreSQL"
        in text
    )
    assert (
        "Alpha database migrations "
        "are not current."
        in text
    )
    assert (
        "não aplica migrações automaticamente"
        in text
    )
    assert (
        "revisões da base de dados validadas "
        "antes do arranque alpha"
        in text
    )
    assert (
        "Google Cloud SQL permanece dependente "
        "da criação do ambiente alpha"
        in text
    )

def test_container_records_source_and_revision():

    text = dockerfile_text()

    assert "ARG VCS_REF=unknown" in text
    assert (
        "org.opencontainers.image.source="
        '"https://github.com/pedroafrade/'
        'PerformanceLab"'
        in text
    )
    assert (
        "org.opencontainers.image.revision="
        '"${VCS_REF}"'
        in text
    )

def test_container_defines_stable_non_root_identity():

    text = dockerfile_text()

    assert "--gid 10001" in text
    assert "--uid 10001" in text
    assert "USER performancelab" in text

    assert (
        text.index("USER performancelab")
        < text.index("CMD [")
    )

def test_container_does_not_define_alpha_configuration():

    text = dockerfile_text()

    forbidden_definitions = (
        "ENV PERFORMANCELAB_ENV=",
        "ENV DATABASE_URL=",
        "ENV PRIVACY_CONTACT_EMAIL=",
        "ENV GEMINI_API_KEY=",
        "ENV BETTER_STACK_ERROR_DSN=",
    )

    for definition in forbidden_definitions:

        assert definition not in text