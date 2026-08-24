"""
Tests for the initial Alembic migration.
"""

import importlib.util

from pathlib import (
    Path,
)

from sqlalchemy import (
    Column,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)


MIGRATION_PATH = (
    Path(__file__).parent.parent
    / "migrations"
    / "versions"
    / (
        "20260823_01_"
        "create_initial_postgresql_schema.py"
    )
)


def load_initial_migration():

    specification = (
        importlib.util
        .spec_from_file_location(
            "initial_postgresql_migration",
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


def test_initial_migration_has_expected_revision():

    migration = load_initial_migration()

    assert (
        migration.revision
        == "20260823_01"
    )
    assert (
        migration.down_revision
        is None
    )


def test_initial_migration_creates_all_schema_tables(
    monkeypatch,
):

    migration = load_initial_migration()

    created_tables = {}

    def create_table(
        table_name,
        *arguments,
        **options,
    ):

        created_tables[
            table_name
        ] = arguments

    monkeypatch.setattr(
        migration.op,
        "create_table",
        create_table,
    )

    migration.upgrade()

    assert tuple(
        created_tables
    ) == (
        "athletes",
        "users",
        "external_identities",
        "user_athlete_access",
        "alpha_invitations",
        "athlete_snapshots",
    )


def test_initial_migration_uses_jsonb_snapshot_payload(
    monkeypatch,
):

    migration = load_initial_migration()

    created_tables = {}

    def create_table(
        table_name,
        *arguments,
        **options,
    ):

        created_tables[
            table_name
        ] = arguments

    monkeypatch.setattr(
        migration.op,
        "create_table",
        create_table,
    )

    migration.upgrade()

    payload_column = next(
        argument
        for argument
        in created_tables[
            "athlete_snapshots"
        ]
        if (
            isinstance(
                argument,
                Column,
            )
            and argument.name
            == "payload"
        )
    )

    assert isinstance(
        payload_column.type,
        JSONB,
    )
    assert (
        payload_column.nullable
        is False
    )


def test_initial_migration_drops_tables_in_reverse_order(
    monkeypatch,
):

    migration = load_initial_migration()

    dropped_tables = []

    monkeypatch.setattr(
        migration.op,
        "drop_table",
        dropped_tables.append,
    )

    migration.downgrade()

    assert dropped_tables == [
        "athlete_snapshots",
        "alpha_invitations",
        "user_athlete_access",
        "external_identities",
        "users",
        "athletes",
    ]