"""
PerformanceLab

Phase G roadmap status tests.
"""

from pathlib import (
    Path,
)


ROADMAP_PATH = (
    Path(__file__).parents[1]
    / "docs"
    / "ROADMAP_PUBLIC_UI.md"
)


def roadmap_text():

    text = ROADMAP_PATH.read_text(
        encoding="utf-8"
    )

    return " ".join(
        text.split()
    )


def test_phase_g_records_current_progress():

    text = roadmap_text()

    assert (
        "10 estão tecnicamente concluídos"
        in text
    )
    assert (
        "1 está implementado, mas aguarda "
        "ativação externa"
        in text
    )
    assert (
        "2 aguardam o ambiente Google Cloud SQL"
        in text
    )


def test_phase_g_preserves_external_blockers():

    text = roadmap_text()

    blockers = (
        "alertas do Better Stack",
        "backups automáticos no Google Cloud SQL",
        "restauro real numa base de dados separada",
        "A fase G não está concluída",
        "os convites permanecem bloqueados",
    )

    for blocker in blockers:

        assert blocker in text


def test_roadmap_records_removed_artifacts():

    text = roadmap_text()

    assert (
        "os antigos artefactos versionados "
        "foram removidos"
        in text
    )
    assert (
        "o `.gitignore` protege dados, segredos, "
        "coberturas, backups e exportações locais"
        in text
    )


def test_google_trial_has_not_started():

    text = roadmap_text()

    assert (
        "evita iniciar prematuramente os 90 dias"
        in text
    )
    assert "300 USD" in text