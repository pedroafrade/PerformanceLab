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


def test_policy_limits_alpha_to_adults():

    text = policy_text()

    assert (
        "18 anos ou mais"
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


def test_policy_discloses_optional_gemini_processing():

    text = policy_text()

    assert "Google Gemini" in text

    assert (
        "autorização separada"
        in text
    )


def test_policy_does_not_claim_to_be_final():

    text = policy_text()

    assert (
        "Este documento ainda não está "
        "pronto para publicação"
        in text
    )