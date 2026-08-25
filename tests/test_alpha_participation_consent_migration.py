"""
Tests for the private alpha consent migration.
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
        "20260825_02_create_alpha_"
        "participation_consents.py"
    )
)


def load_migration():

    specification = (
        importlib.util
        .spec_from_file_location(
            (
                "alpha_participation_"
                "consent_migration"
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


def test_alpha_consent_migration_revision_chain():

    migration = load_migration()

    assert (
        migration.revision
        == "20260825_02"
    )

    assert (
        migration.down_revision
        == "20260825_01"
    )


def test_alpha_consent_migration_creates_and_drops_table(
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
        "alpha_participation_consents",
    ]

    assert dropped_tables == [
        "alpha_participation_consents",
    ]