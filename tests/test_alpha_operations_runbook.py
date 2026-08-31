"""
PerformanceLab

Private alpha operations runbook tests.
"""

from pathlib import (
    Path,
)


RUNBOOK_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ALPHA_OPERATIONS_RUNBOOK.md"
)


def runbook_text():

    text = RUNBOOK_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        text.split()
    )


def test_runbook_records_release_checks():

    text = runbook_text()

    required_checks = (
        "pytest -q",
        "git status --short",
        "git diff --check",
        "git log -1 --oneline",
        "Nunca utilizar `git add .`",
    )

    for check in required_checks:

        assert check in text


def test_runbook_records_migration_commands():

    text = runbook_text()

    commands = (
        "alembic current",
        "alembic heads",
        "alembic upgrade head",
        "`DATABASE_URL`",
    )

    for command in commands:

        assert command in text


def test_runbook_requires_safe_rollback():

    text = runbook_text()

    assert (
        "Não utilizar `git reset --hard`"
        in text
    )
    assert (
        "Não executar automaticamente"
        in text
    )
    assert (
        "restaurar o backup numa base separada"
        in text
    )
    assert (
        "Nunca testar um restauro diretamente "
        "sobre a base ativa"
        in text
    )


def test_runbook_covers_incident_response():

    text = runbook_text()

    required_actions = (
        "suspender a aplicação e os convites",
        "identificador de correlação",
        "avaliar participantes e dados afetados",
        "testar antes de reabrir",
        "obrigações de comunicação",
    )

    for action in required_actions:

        assert action in text


def test_runbook_forbids_secrets():

    text = runbook_text()

    protected_values = (
        "Passwords",
        "tokens",
        "chaves",
        "certificados",
        "valores reais de `DATABASE_URL`",
    )

    for value in protected_values:

        assert value in text


def test_runbook_preserves_pending_blockers():

    text = runbook_text()

    pending_items = (
        "revisão jurídica externa concluída",
        "avaliação Google Cloud iniciada",
        "backups automáticos ativos",
        "restauro real testado",
        "deployment executado",
    )

    for item in pending_items:

        assert f"- [ ] {item}" in text

def test_runbook_records_confirmed_google_cloud_services():

    text = runbook_text()

    assert "Google Cloud Run" in text
    assert "Google Cloud SQL PostgreSQL" in text
    assert "Google Secret Manager" in text
    assert "região da União Europeia" in text
    assert (
        "fornecedor de alojamento da aplicação "
        "ainda está por confirmar"
        not in text
    )


def test_runbook_requires_all_alpha_preflights():

    text = runbook_text()

    preflights = (
        "check_alpha_configuration.py",
        "check_alpha_auth_configuration.py",
        "check_alpha_database.py",
        "check_alpha_migrations.py",
    )

    for preflight in preflights:

        assert preflight in text

    assert (
        "Alpha database migrations are current."
        in text
    )
    assert (
        "Não se deve contornar o preflight"
        in text
    )


def test_runbook_preserves_cloud_activation_boundary():

    text = runbook_text()

    assert "não ativa a Google Cloud" in text
    assert "não cria custos" in text
    assert (
        "não inicia o período experimental"
        in text
    )

def test_runbook_formats_migration_result_as_text():

    source = RUNBOOK_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "```text\n"
        "Alpha database migrations are current.\n"
        "```"
        in source
    )
    assert (
        "Nota: no editor, confirma que os blocos"
        not in source
    )


def test_runbook_marks_cloud_run_selection_complete():

    source = RUNBOOK_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "- [x] Google Cloud Run escolhido "
        "para alojar a aplicação;"
        in source
    )
    assert (
        "- [ ] alojamento da aplicação escolhido;"
        not in source
    )

def test_runbook_records_automatic_image_guarantees():

    text = runbook_text()

    guarantees = (
        "label OCI da revisão",
        "utilizador `performancelab`",
        "UID não-root `10001`",
        "não são graváveis pelo utilizador runtime",
        "configuração OIDC real",
        "valores de configuração alpha",
        "endpoint de saúde responde",
        "recusadas antes do Streamlit",
    )

    for guarantee in guarantees:

        assert guarantee in text


def test_runbook_requires_immutable_deployment_image():

    text = runbook_text()

    assert "publicar a imagem sem a reconstruir" in text
    assert "digest imutável" in text
    assert (
        "publicar no Cloud Run exatamente "
        "esse digest"
        in text
    )
    assert (
        "registar o digest e o commit"
        in text
    )


def test_runbook_preserves_image_publication_boundary():

    text = runbook_text()

    assert "A CI atual não publica imagens" in text
    assert "não contacta a Google Cloud" in text
    assert "não cria recursos" in text
    assert "não inicia custos" in text

def test_runbook_references_deployment_record_template():

    text = runbook_text()

    assert (
        "docs/ALPHA_DEPLOYMENT_RECORD_TEMPLATE.md"
        in text
    )
    assert (
        "O modelo versionado permanece vazio"
        in text
    )
    assert (
        "não deve ser substituído por um "
        "relatório preenchido"
        in text
    )

def test_runbook_requires_image_reference_preflight():

    text = runbook_text()

    required_content = (
        "DEPLOYMENT_IMAGE_REFERENCE",
        "check_alpha_image_reference.py",
        "Alpha deployment image reference "
        "is immutable.",
        "tag mutável",
        "Uma falha bloqueia o deployment",
        "não contacta o registo",
    )

    for content in required_content:

        assert content in text

    assert (
        "não inicia custos"
        in text
    )

def test_runbook_defines_device_ui_validation():

    text = runbook_text()

    environments = (
        "navegador desktop suportado",
        "dispositivo Android",
        "dispositivo iOS",
    )

    for environment in environments:

        assert environment in text

    required_checks = (
        "login e logout",
        "conta sem convite",
        "contacto de suporte",
        "ausência de deslocamento horizontal",
        "importação de um FIT descartável",
        "edição e eliminação",
        "dados de outra conta interna",
    )

    for check in required_checks:

        assert check in text

    assert (
        "bloqueia os convites"
        in text
    )
    assert (
        "Não devem ser guardadas capturas "
        "com emails"
        in text
    )

