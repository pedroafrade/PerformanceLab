"""
Tests for the private alpha privacy policy draft.
"""

from pathlib import (
    Path,
)


POLICY_PATH = (
    Path(__file__).parent.parent
    / "docs"
    / "PRIVACY_POLICY_ALPHA_DRAFT.md"
)


def policy_text() -> str:

    return POLICY_PATH.read_text(
        encoding="utf-8"
    )


def test_policy_is_explicitly_a_draft():

    text = policy_text()

    assert (
        "RASCUNHO — NÃO PUBLICAR"
        in text
    )

    assert (
        "[POR DEFINIR"
        in text
    )


def test_policy_limits_alpha_to_adults_and_invited_users():

    text = policy_text()

    assert (
        "18 anos ou mais"
        in text
    )

    assert (
        "Não existe inscrição pública livre."
        in text
    )


def test_policy_contains_required_sections():

    text = policy_text()

    required_sections = (
        "Responsável pelo tratamento",
        "Dados pessoais tratados",
        "Finalidades",
        "Fundamento jurídico",
        "Fornecedores e destinatários",
        "Transferências internacionais",
        "Conservação",
        "Direitos dos participantes",
        "Retirada da participação",
        "Segurança",
        "Bloqueadores de publicação",
    )

    for section in required_sections:

        assert section in text


def test_policy_documents_confirmed_external_services():

    text = policy_text()

    assert (
        "Google — autenticação OIDC"
        in text
    )

    assert (
        "Google Gemini — Training Coach"
        in text
    )

    assert (
        "gemini-3.5-flash"
        in text
    )


def test_policy_discloses_optional_gemini_processing():

    text = policy_text()

    assert (
        "Esta funcionalidade é opcional"
        in text
    )

    assert (
        "autorização específica"
        in text
    )

    assert (
        "O ficheiro original da atividade "
        "não é enviado ao Gemini."
        in text
    )


def test_policy_documents_alpha_postgresql_requirement():

    text = policy_text()

    assert (
        "exige uma base de dados PostgreSQL"
        in text
    )

    assert (
        "não pode utilizar os repositórios "
        "JSON locais"
        in text
    )


def test_policy_documents_confirmed_retention_rules():

    text = policy_text()

    assert (
        "os ficheiros originais de atividade "
        "não são conservados"
        in text
    )

    assert (
        "apenas a interpretação mais recente "
        "do Training Coach"
        in text
    )

    assert (
        "ao eliminar uma atividade"
        in text
    )


def test_policy_keeps_external_decisions_pending():

    text = policy_text()

    pending_fields = (
        "[POR DEFINIR — RESPONSÁVEL PELO TRATAMENTO]",
        "[POR DEFINIR — EMAIL DE PRIVACIDADE]",
        "[POR DEFINIR — ALOJAMENTO]",
        "[POR DEFINIR — BASE DE DADOS]",
        "[POR DEFINIR — REGIÃO DA APLICAÇÃO]",
        "[POR DEFINIR — REGIÃO DA BASE DE DADOS]",
        "[POR DEFINIR — LOCALIZAÇÃO DOS BACKUPS]",
        "[POR DEFINIR — TRANSFERÊNCIAS E GARANTIAS]",
        "[POR DEFINIR — PRAZOS DE CONSERVAÇÃO]",
        "[POR DEFINIR — PRAZO DE RESPOSTA]",
    )

    for field in pending_fields:

        assert field in text


def test_policy_does_not_claim_to_be_final():

    text = policy_text()

    assert (
        "Este documento ainda não está "
        "pronto para publicação"
        in text
    )

    assert (
        "revisão jurídica final"
        in text
    )

def test_privacy_policy_references_retention_schedule():

    text = policy_text()

    assert (
        "docs/RETENTION_POLICY_ALPHA_DRAFT.md"
        in text
    )

    assert (
        "impede o arranque do ambiente alpha"
        in text
    )