"""
PerformanceLab

Privacy phase transition documentation tests.
"""

from pathlib import (
    Path,
)


ROADMAP_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ROADMAP_PUBLIC_UI_260825.md"
)


def roadmap_text() -> str:

    source = ROADMAP_PATH.read_text(
        encoding="utf-8",
    )

    return " ".join(
        source.split()
    )

def test_legal_review_remains_explicitly_pending():

    text = roadmap_text()

    assert (
        "| F — Privacidade e controlo | "
        "**8/9** | revisão jurídica pendente |"
        in text
    )
    assert (
        "revisão jurídica externa pendente"
        in text
    )


def test_legal_review_blocks_real_participant_invitations():

    text = roadmap_text()

    assert (
        "impede a publicação final dos textos"
        in text
    )
    assert (
        "qualquer convite a participantes reais"
        in text
    )
    assert (
        "Os convites permanecem bloqueados"
        in text
    )


def test_technical_work_can_continue_during_review():

    text = roadmap_text()

    assert (
        "não impede a continuação do trabalho "
        "técnico das fases G e H"
        in text
    )