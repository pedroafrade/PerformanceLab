"""
Tests for the private alpha retention policy draft.
"""

from pathlib import (
    Path,
)


POLICY_PATH = (
    Path(__file__).parent.parent
    / "docs"
    / "RETENTION_POLICY_ALPHA_DRAFT.md"
)


def policy_text() -> str:

    return POLICY_PATH.read_text(
        encoding="utf-8"
    )


def test_retention_policy_is_explicitly_a_draft():

    text = policy_text()

    assert (
        "RASCUNHO — NÃO ATIVAR NA ALPHA"
        in text
    )

    assert (
        "[POR DEFINIR"
        in text
    )


def test_retention_policy_covers_required_categories():

    text = policy_text()

    categories = (
        "Contas e perfis ativos",
        "Ficheiros de atividade importados",
        "Interpretações do Training Coach",
        "Metadados de utilização do Training Coach",
        "Consentimentos",
        "Convites",
        "Logs de aplicação e segurança",
        "Erros e alertas",
        "Backups",
        "Exportações",
        "Pedidos de suporte e exercício de direitos",
        "Fim da alpha privada",
    )

    for category in categories:

        assert category in text


def test_retention_policy_records_confirmed_rules():

    text = policy_text()

    confirmed_rules = (
        "eliminação no final do processamento",
        "apenas a interpretação mais recente por atividade",
        "Não são conservados prompts completos",
        "não deverá guardar uma cópia adicional da exportação",
        "transação",
    )

    for rule in confirmed_rules:

        assert rule in text


def test_retention_policy_does_not_invent_pending_periods():

    text = policy_text()

    pending_periods = (
        "[POR DEFINIR — PRAZO PARA CONTAS INATIVAS]",
        "[POR DEFINIR — RETENÇÃO DOS METADADOS DO TRAINING COACH]",
        "[POR DEFINIR — VALIDADE DO CONVITE]",
        "[POR DEFINIR — RETENÇÃO DOS LOGS]",
        "[POR DEFINIR — RETENÇÃO DOS BACKUPS]",
        "[POR DEFINIR — RETENÇÃO DE PEDIDOS E SUPORTE]",
        "[POR DEFINIR — PRAZO APÓS O FIM DA ALPHA]",
    )

    for period in pending_periods:

        assert period in text


def test_retention_policy_addresses_deleted_data_in_backups():

    text = policy_text()

    assert (
        "poderão permanecer temporariamente "
        "num backup"
        in text
    )

    assert (
        "não deverá reativar silenciosamente "
        "contas ou dados previamente eliminados"
        in text
    )