"""
PerformanceLab

Google Cloud SQL alpha decision tests.
"""

from pathlib import (
    Path,
)


POLICY_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "GOOGLE_CLOUD_SQL_ALPHA.md"
)


def policy_text():

    text = POLICY_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        text.split()
    )


def test_records_google_cloud_sql_decision():

    text = policy_text()

    assert (
        "Google Cloud SQL for PostgreSQL"
        in text
    )
    assert (
        "FORNECEDOR ESCOLHIDO"
        in text
    )
    assert (
        "ATIVAÇÃO PENDENTE"
        in text
    )


def test_records_trial_limits():

    text = policy_text()

    assert "300 USD" in text
    assert "90 dias" in text
    assert "Dia 0" in text
    assert "Dias 0–20" in text
    assert "Dia 21" in text
    assert (
        "fim obrigatório da alpha "
        "com participantes"
        in text
    )
    assert "Dias 61–75" in text
    assert "Dia 85" in text
    assert "Dias 86–90" in text
    assert "limite absoluto" in text
    assert "Activate ou Ativar" in text


def test_records_budget_alerts():

    text = policy_text()

    assert "150 USD" in text
    assert "225 USD" in text
    assert "270 USD" in text
    assert (
        "Não garantem que os serviços sejam"
        in text
    )
    assert (
        "automaticamente interrompidos"
        in text
    )


def test_requires_backup_protection():

    text = policy_text()

    requirements = (
        "região pertencente à União Europeia",
        "backups automáticos diários",
        "retenção de backups durante 14 dias",
        "ligação encriptada",
        "instância separada",
    )

    for requirement in requirements:

        assert requirement in text


def test_preserves_postgresql_portability():

    text = policy_text()

    portability_items = (
        "PostgreSQL normal",
        "SQLAlchemy",
        "Psycopg 3",
        "migrações Alembic",
        "`DATABASE_URL`",
        "outro serviço PostgreSQL",
    )

    for item in portability_items:

        assert item in text


def test_does_not_claim_external_activation():

    text = policy_text()

    pending_items = (
        "conta Google Cloud criada",
        "região europeia confirmada",
        "instância PostgreSQL criada",
        "alertas de orçamento criados",
        "backups automáticos configurados",
        "restauro real testado",
    )

    for item in pending_items:

        assert f"- [ ] {item}" in text