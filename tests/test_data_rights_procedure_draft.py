"""
Tests for the private alpha data-rights procedure draft.
"""

from pathlib import (
    Path,
)


PROCEDURE_PATH = (
    Path(__file__).parent.parent
    / "docs"
    / "DATA_RIGHTS_PROCEDURE_ALPHA_DRAFT.md"
)


def procedure_text() -> str:

    return PROCEDURE_PATH.read_text(
        encoding="utf-8"
    )


def test_procedure_is_explicitly_a_draft():

    text = procedure_text()

    assert (
        "RASCUNHO — CONTACTO DE "
        "PRIVACIDADE PENDENTE"
        in text
    )

    assert (
        "[POR DEFINIR — EMAIL DE PRIVACIDADE]"
        in text
    )


def test_procedure_covers_participant_rights():

    text = procedure_text()

    required_rights = (
        "Pedido de acesso",
        "Pedido de correção",
        "Pedido de exportação ou portabilidade",
        "Pedido de eliminação",
        "Limitação do tratamento",
        "Oposição",
        "Retirada de consentimento",
    )

    for right in required_rights:

        assert right in text


def test_procedure_defines_response_deadline():

    text = procedure_text()

    assert (
        "um mês após a receção do pedido"
        in text
    )

    assert (
        "prorrogado por até mais dois meses"
        in text
    )

    assert (
        "dentro do primeiro mês"
        in text
    )


def test_procedure_uses_approved_retention_periods():

    text = procedure_text()

    assert (
        "RETENTION_SUPPORT_REQUEST_DAYS=90"
        in text
    )

    assert (
        "RETENTION_BACKUP_DAYS=14"
        in text
    )


def test_procedure_requires_identity_verification():

    text = procedure_text()

    assert (
        "endereço de email verificado "
        "associado à identidade OIDC"
        in text
    )

    assert (
        "Não deverá ser pedida automaticamente "
        "uma cópia de documento de identificação"
        in text
    )


def test_procedure_prohibits_sensitive_request_logs():

    text = procedure_text()

    prohibited_content = (
        "passwords",
        "tokens",
        "prompts completos",
        "ficheiros importados",
        "exportações completas",
        "payload fisiológico",
    )

    for item in prohibited_content:

        assert item in text


def test_procedure_requires_disposable_rehearsal():

    text = procedure_text()

    assert (
        "contas descartáveis"
        in text
    )

    assert (
        "não deverá utilizar dados pessoais reais"
        in text
    )