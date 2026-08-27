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

    assert "Dos 15 requisitos anteriores" in text
    assert (
        "9 estão tecnicamente concluídos"
        in text
    )
    assert (
        "3 estão implementados, mas "
        "aguardam validação externa"
        in text
    )
    assert (
        "3 permanecem pendentes"
        in text
    )


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
        "Os convites permanecem bloqueados",
    )

    for blocker in blockers:

        assert blocker in text


def test_phase_h_preserves_trial_boundary():

    text = roadmap_text()

    assert "não cria recursos Google Cloud" in text
    assert "não inicia custos" in text
    assert (
        "não inicia o período experimental "
        "de 90 dias"
        in text
    )

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
        "23fef66"
        in text
    )