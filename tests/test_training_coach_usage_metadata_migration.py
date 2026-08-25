"""
Tests for the Training Coach metadata migration.
"""

import importlib.util

from pathlib import (
    Path,
)


MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "migrations"
    / "versions"
    / (
        "20260825_01_add_training_"
        "coach_usage_metadata.py"
    )
)


def load_migration():

    specification = (
        importlib.util
        .spec_from_file_location(
            (
                "training_coach_usage_"
                "metadata_migration"
            ),
            MIGRATION_PATH,
        )
    )

    assert specification is not None
    assert specification.loader is not None

    migration = (
        importlib.util
        .module_from_spec(
            specification
        )
    )

    specification.loader.exec_module(
        migration
    )

    return migration


def test_metadata_migration_revision_chain():

    migration = load_migration()

    assert (
        migration.revision
        == "20260825_01"
    )

    assert (
        migration.down_revision
        == "20260824_03"
    )


def test_metadata_migration_adds_and_removes_columns(
    monkeypatch,
):

    migration = load_migration()

    added_columns = []
    removed_columns = []

    def add_column(
        table_name,
        column,
    ):

        added_columns.append(
            (
                table_name,
                column.name,
            )
        )

    def drop_column(
        table_name,
        column_name,
    ):

        removed_columns.append(
            (
                table_name,
                column_name,
            )
        )

    monkeypatch.setattr(
        migration.op,
        "add_column",
        add_column,
    )

    monkeypatch.setattr(
        migration.op,
        "drop_column",
        drop_column,
    )

    migration.upgrade()
    migration.downgrade()

    assert added_columns == [
        (
            "training_coach_usage",
            "provider",
        ),
        (
            "training_coach_usage",
            "model",
        ),
        (
            "training_coach_usage",
            "error_code",
        ),
        (
            "training_coach_usage",
            "latency_ms",
        ),
        (
            "training_coach_usage",
            "remaining_user_requests",
        ),
        (
            "training_coach_usage",
            "remaining_global_requests",
        ),
    ]

    assert removed_columns == [
        (
            "training_coach_usage",
            "remaining_global_requests",
        ),
        (
            "training_coach_usage",
            "remaining_user_requests",
        ),
        (
            "training_coach_usage",
            "latency_ms",
        ),
        (
            "training_coach_usage",
            "error_code",
        ),
        (
            "training_coach_usage",
            "model",
        ),
        (
            "training_coach_usage",
            "provider",
        ),
    ]