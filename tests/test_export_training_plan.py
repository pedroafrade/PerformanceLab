"""
Tests for the standalone training-plan exporter.
"""

import json
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[1]
)

EXPORT_SCRIPT = (
    PROJECT_ROOT
    / "export_training_plan.py"
)


def _write_athlete(
    path: Path,
    *,
    start_date: str,
) -> None:
    """
    Writes the minimum athlete data required by the
    standalone exporter.
    """

    path.write_text(
        json.dumps(
            {
                "training_plan": {
                    "start_date": (
                        start_date
                    ),
                    "end_date": (
                        "2026-10-04"
                    ),
                    "workouts": [],
                }
            }
        ),
        encoding="utf-8",
    )


def test_export_ignores_athlete_backup_files(
    tmp_path,
):

    athletes_directory = (
        tmp_path
        / "data"
        / "athletes"
    )

    athletes_directory.mkdir(
        parents=True
    )

    _write_athlete(
        athletes_directory
        / "athlete.backup.json",
        start_date="2026-08-01",
    )

    _write_athlete(
        athletes_directory
        / "athlete.backup-adaptation.json",
        start_date="2026-08-05",
    )

    _write_athlete(
        athletes_directory
        / "athlete.json",
        start_date="2026-08-13",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(EXPORT_SCRIPT),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )

    exported_plan = (
        tmp_path
        / "PLANO_DE_TREINO.txt"
    )

    assert exported_plan.exists()

    content = exported_plan.read_text(
        encoding="utf-8-sig"
    )

    assert (
        "Start: 2026-08-13"
        in content
    )

    assert (
        "Start: 2026-08-01"
        not in content
    )

    assert (
        "Start: 2026-08-05"
        not in content
    )

    assert (
        "Created:"
        in result.stdout
    )


def test_export_fails_without_primary_athlete_file(
    tmp_path,
):

    athletes_directory = (
        tmp_path
        / "data"
        / "athletes"
    )

    athletes_directory.mkdir(
        parents=True
    )

    _write_athlete(
        athletes_directory
        / "athlete.backup.json",
        start_date="2026-08-01",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(EXPORT_SCRIPT),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0

    assert (
        "No athlete file found "
        "in data/athletes."
        in (
            result.stdout
            + result.stderr
        )
    )

    assert not (
        tmp_path
        / "PLANO_DE_TREINO.txt"
    ).exists()