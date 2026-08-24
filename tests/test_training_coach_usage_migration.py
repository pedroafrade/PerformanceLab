"""
Tests for the Training Coach usage migration.
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
        "20260824_03_"
        "create_training_coach_usage.py"
    )
)


def load_migration():

    specification = (
        importlib.util
        .spec_from_file_location(
            "training_coach_usage_migration",
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


def test_usage_migration_revision_chain():

    migration = load_migration()

    assert (
        migration.revision
        == "20260824_03"
    )

    assert (
        migration.down_revision
        == "20260824_02"
    )


def test_usage_migration_creates_and_drops_table(
    monkeypatch,
):

    migration = load_migration()

    created_tables = []
    dropped_tables = []

    def create_table(
        table_name,
        *arguments,
        **options,
    ):

        created_tables.append(
            table_name
        )

    monkeypatch.setattr(
        migration.op,
        "create_table",
        create_table,
    )

    monkeypatch.setattr(
        migration.op,
        "drop_table",
        dropped_tables.append,
    )

    migration.upgrade()
    migration.downgrade()

    assert created_tables == [
        "training_coach_usage",
    ]

    assert dropped_tables == [
        "training_coach_usage",
    ]