"""Tests for the login-time athlete provisioning migration."""

import importlib.util
from pathlib import Path
from unittest.mock import MagicMock


MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "versions"
    / "20260924_01_allow_login_time_athlete_provisioning.py"
)


def load_migration():
    specification = importlib.util.spec_from_file_location(
        "login_time_athlete_migration",
        MIGRATION,
    )
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def test_migration_relaxes_and_restores_invitation_constraint(monkeypatch):
    migration = load_migration()
    operation = MagicMock()
    monkeypatch.setattr(migration, "op", operation)

    assert migration.revision == "20260924_01"
    assert migration.down_revision == "20260904_04"

    migration.upgrade()
    operation.drop_constraint.assert_called_once_with(
        "ck_alpha_invitations_athlete_invitation_has_athlete",
        "alpha_invitations",
        type_="check",
    )

    migration.downgrade()
    operation.create_check_constraint.assert_called_once_with(
        "ck_alpha_invitations_athlete_invitation_has_athlete",
        "alpha_invitations",
        "role <> 'athlete' OR athlete_id IS NOT NULL",
    )
