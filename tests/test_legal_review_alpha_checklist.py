"""
Tests for the private alpha legal-review checklist.
"""

from pathlib import (
    Path,
)


CHECKLIST_PATH = (
    Path(__file__).parent.parent
    / "docs"
    / "LEGAL_REVIEW_ALPHA_CHECKLIST.md"
)


def checklist_text() -> str:

    return CHECKLIST_PATH.read_text(
        encoding="utf-8"
    )


def test_checklist_does_not_claim_legal_approval():

    text = checklist_text()

    assert (
        "REVISÃO EXTERNA PENDENTE"
        in text
    )

    assert (
        "REVISÃO EXTERNA NÃO REALIZADA"
        in text
    )

    assert (
        "não significa que a política "
        "foi revista ou aprovada"
        in text
    )


def test_checklist_references_review_documents():

    text = checklist_text()

    documents = (
        "docs/PRIVACY_POLICY_ALPHA_DRAFT.md",
        "docs/RETENTION_POLICY_ALPHA_DRAFT.md",
        "docs/DATA_RIGHTS_PROCEDURE_ALPHA_DRAFT.md",
        "docs/ROADMAP_PUBLIC_UI_260825.md",
    )

    for document in documents:

        assert document in text


def test_checklist_covers_required_legal_questions():

    text = (
        checklist_text()
        .casefold()
    )

    required_questions = (
        "fundamentos jurídicos",
        "consentimento da alpha",
        "training coach e google gemini",
        "fornecedores e subprocessadores",
        "transferências internacionais",
        "conservação",
        "direitos dos participantes",
        "exportação",
        "eliminação",
        "decisões automatizadas e recomendações",
        "segurança e incidentes",
        "avaliação de impacto",
    )

    for question in required_questions:

        assert question in text


def test_checklist_preserves_pending_review_record():

    text = checklist_text()

    pending_fields = (
        "Revisor: `[PENDENTE]`",
        "Organização: `[PENDENTE]`",
        "Data: `[PENDENTE]`",
        "Documentos e versões revistos: `[PENDENTE]`",
        "Resultado: `[PENDENTE",
    )

    for field in pending_fields:

        assert field in text


def test_checklist_requires_real_external_review():

    text = checklist_text()

    requirements = (
        "existir um revisor jurídico identificado",
        "as decisões estiverem documentadas",
        "as alterações necessárias forem aplicadas",
        "o resultado da revisão estiver registado",
    )

    for requirement in requirements:

        assert requirement in text