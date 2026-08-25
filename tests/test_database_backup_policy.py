"""
PerformanceLab

Database backup policy tests.
"""

from pathlib import (
    Path,
)


POLICY_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "DATABASE_BACKUPS.md"
)


def policy_text():

    return POLICY_PATH.read_text(
        encoding="utf-8"
    )


def test_backup_policy_records_required_protection():

    text = policy_text()

    requirements = (
        "backups automáticos",
        "armazenamento encriptado",
        "comunicação encriptada",
        "União Europeia",
        "14 dias",
        "eliminação automática",
        "base de dados separada",
    )

    for requirement in requirements:

        assert requirement in text


def test_backup_policy_does_not_claim_activation():

    text = policy_text()

    pending_statements = (
        "CONFIGURAÇÃO EXTERNA PENDENTE",
        "fornecedor PostgreSQL ainda não foi escolhido",
        "backups automáticos ainda não estão ativos",
        "ainda não existe um restauro testado",
    )

    for statement in pending_statements:

        assert statement in text


def test_backup_policy_forbids_secrets_and_local_copies():

    text = policy_text()

    protected_values = (
        "passwords",
        "tokens",
        "chaves",
        "`DATABASE_URL`",
        "ficheiros de backup descarregados",
    )

    for value in protected_values:

        assert value in text

    assert (
        "Não devem ser criadas cópias locais manuais"
        in text
    )


def test_backup_policy_protects_deleted_data():

    text = policy_text()

    assert (
        "não pode reativar silenciosamente"
        in text
    )
    assert (
        "reconciliar as eliminações"
        in text
    )


def test_backup_policy_keeps_restore_separate():

    text = policy_text()

    assert (
        "nunca deverá ser restaurado diretamente"
        in text
    )
    assert (
        "passo G.8"
        in text
    )