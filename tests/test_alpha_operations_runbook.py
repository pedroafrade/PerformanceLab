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
        "alojamento da aplicação escolhido",
        "avaliação Google Cloud iniciada",
        "backups automáticos ativos",
        "restauro real testado",
        "deployment executado",
    )

    for item in pending_items:

        assert f"- [ ] {item}" in text