"""
PerformanceLab

Current phase H roadmap status tests.
"""

from pathlib import (
    Path,
)


ROADMAP_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ROADMAP_PUBLIC_UI_260825.md"
)


def roadmap_text():

    source = ROADMAP_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        source.split()
    )


def test_phase_h_records_current_progress():

    text = roadmap_text()

    assert "alpha privada online" in text
    assert "bfc40a9" in text
    assert "Implementado" in text
    assert "Publicado" in text
    assert "Validado em operação" in text
    assert "Os convites permanecem bloqueados" not in text

def test_phase_h_records_cloud_run_strategy():

    text = roadmap_text()

    assert "Google Cloud Run" in text
    assert "Google Cloud SQL PostgreSQL" in text
    assert "Google Secret Manager" in text
    assert "região da União Europeia" in text


def test_phase_h_preserves_blockers():

    text = roadmap_text()

    blockers = (
        "revisão jurídica externa",
        "Better Stack",
        "backup automático",
        "restauro real",
        "contacto de suporte visível",
        "desktop, Android e iOS",
    )

    for blocker in blockers:

        assert blocker in text


def test_phase_h_separates_documentation_from_external_execution():

    text = roadmap_text()

    assert "não executa deployment" in text
    assert "nem certifica controlos externos" in text
    assert "Better Stack passou a ser opcional" in text

def test_phase_h_records_alpha_startup_preflights():

    text = roadmap_text()

    assert (
        "configuração runtime, a configuração "
        "OIDC, a ligação PostgreSQL e as "
        "revisões das migrações"
        in text
    )
    assert (
        "antes de iniciar o Streamlit"
        in text
    )
    assert (
        "bfc40a9"
        in text
    )
