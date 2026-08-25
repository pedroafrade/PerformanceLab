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


def test_retention_policy_is_pending_legal_review():

    text = policy_text()

    assert (
        "RASCUNHO — PRAZOS APROVADOS, "
        "REVISÃO JURÍDICA PENDENTE"
        in text
    )

    assert (
        "[POR DEFINIR"
        not in text
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

def test_retention_decisions_map_to_configuration():

    text = policy_text()

    configuration_names = (
        "RETENTION_INACTIVE_ACCOUNT_DAYS",
        "RETENTION_INACTIVITY_NOTICE_DAYS",
        "RETENTION_TRAINING_COACH_USAGE_DAYS",
        "RETENTION_CONSENT_EVIDENCE_DAYS",
        "RETENTION_UNUSED_INVITATION_DAYS",
        "RETENTION_EXPIRED_INVITATION_DAYS",
        "RETENTION_APPLICATION_LOG_DAYS",
        "RETENTION_ERROR_ALERT_DAYS",
        "RETENTION_BACKUP_DAYS",
        "RETENTION_SUPPORT_REQUEST_DAYS",
        "RETENTION_POST_ALPHA_DAYS",
    )

    for configuration_name in configuration_names:

        assert configuration_name in text

def test_retention_policy_contains_approved_periods():

    text = policy_text()

    approved_settings = (
        "RETENTION_INACTIVE_ACCOUNT_DAYS=90",
        "RETENTION_INACTIVITY_NOTICE_DAYS=14",
        "RETENTION_TRAINING_COACH_USAGE_DAYS=30",
        "RETENTION_CONSENT_EVIDENCE_DAYS=0",
        "RETENTION_UNUSED_INVITATION_DAYS=14",
        "RETENTION_EXPIRED_INVITATION_DAYS=7",
        "RETENTION_APPLICATION_LOG_DAYS=14",
        "RETENTION_ERROR_ALERT_DAYS=30",
        "RETENTION_BACKUP_DAYS=14",
        "RETENTION_SUPPORT_REQUEST_DAYS=90",
        "RETENTION_POST_ALPHA_DAYS=30",
    )

    for setting in approved_settings:

        assert setting in text