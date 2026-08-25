"""
PerformanceLab

Privacy phase transition documentation tests.
"""

from pathlib import Path


ROADMAP_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ROADMAP_PUBLIC_UI.md"
)


def roadmap_text() -> str:

    return ROADMAP_PATH.read_text(
        encoding="utf-8",
    )


def test_legal_review_remains_explicitly_pending():

    text = roadmap_text()

    assert "8 de 9 passos concluídos" in text
    assert "passo 9.2" in text
    assert "temporariamente pendente" in text
    assert "revisão jurídica externa" in text


def test_legal_review_blocks_real_participant_invitations():

    text = roadmap_text()

    assert (
        "Antes do primeiro convite "
        "a participantes reais"
        in text
    )

    assert (
        "a fase F não deve ser considerada "
        "integralmente concluída"
        in text
    )


def test_phase_g_can_start_while_review_is_pending():

    text = roadmap_text()

    assert (
        "avançar com o trabalho técnico "
        "da fase G"
        in text
    )