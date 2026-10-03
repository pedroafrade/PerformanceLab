"""
PerformanceLab

Privacy review requirements for the online private alpha.
"""

from pathlib import Path


ROADMAP_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ROADMAP_PUBLIC_UI_260825.md"
)


def roadmap_text() -> str:
    return " ".join(
        ROADMAP_PATH.read_text(encoding="utf-8").split()
    )


def test_online_alpha_does_not_certify_legal_review():
    text = roadmap_text()

    assert "alpha privada online" in text
    assert "revisão jurídica externa" in text
    assert (
        "A alpha online não comprova que a revisão tenha sido concluída."
        in text
    )
    assert "nem certifica controlos externos" in text


def test_pending_legal_review_blocks_publication_and_new_invitations():
    text = roadmap_text()

    assert (
        "um requisito antes da publicação final dos textos "
        "e de novos convites a participantes reais"
        in text
    )
    assert (
        "Se estiver pendente, essas ações permanecem bloqueadas."
        in text
    )


def test_technical_work_does_not_presume_legal_approval():
    text = roadmap_text()

    assert (
        "O trabalho técnico pode continuar sem presumir aprovação jurídica "
        "ou autorizar novos convites."
        in text
    )
