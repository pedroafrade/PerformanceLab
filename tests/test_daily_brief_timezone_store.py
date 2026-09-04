from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, insert

from performancelab.storage.daily_brief_timezone_store import (
    DailyBriefTimezoneStore,
)
from performancelab.storage.postgresql_schema import (
    daily_brief_timezones,
    users,
)


NOW = datetime(2026, 9, 4, 12, tzinfo=timezone.utc)
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def database():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    users.create(engine)
    daily_brief_timezones.create(engine)
    with engine.begin() as connection:
        connection.execute(insert(users).values(
            user_id="user-1",
            email="athlete@example.test",
            role="athlete",
        ))
    return engine


def test_missing_timezone_is_explicit_instead_of_assuming_server_time(database):
    with database.connect() as connection:
        assert DailyBriefTimezoneStore(connection).get(user_id="user-1") is None


def test_confirms_and_replaces_valid_iana_timezone(database):
    with database.begin() as connection:
        store = DailyBriefTimezoneStore(connection)
        first = store.confirm(
            user_id="user-1",
            timezone_name="Europe/Lisbon",
            confirmed_at=NOW,
        )
        second = store.confirm(
            user_id="user-1",
            timezone_name="Atlantic/Azores",
            confirmed_at=NOW,
        )

        assert first.timezone_name == "Europe/Lisbon"
        assert second.timezone_name == "Atlantic/Azores"
        assert store.get(user_id="user-1") == second


@pytest.mark.parametrize(
    "timezone_name",
    ("", "Europe/NotARealCity", "../Lisbon", "*"),
)
def test_rejects_invalid_timezone_without_changing_existing_value(
    database,
    timezone_name,
):
    with database.begin() as connection:
        store = DailyBriefTimezoneStore(connection)
        original = store.confirm(
            user_id="user-1",
            timezone_name="Europe/Lisbon",
            confirmed_at=NOW,
        )
        with pytest.raises(ValueError):
            store.confirm(
                user_id="user-1",
                timezone_name=timezone_name,
                confirmed_at=NOW,
            )
        assert store.get(user_id="user-1") == original


def test_timezone_preference_can_be_deleted(database):
    with database.begin() as connection:
        store = DailyBriefTimezoneStore(connection)
        store.confirm(
            user_id="user-1",
            timezone_name="Europe/Lisbon",
            confirmed_at=NOW,
        )
        store.delete(user_id="user-1")
        assert store.get(user_id="user-1") is None


def test_schema_and_migration_delete_timezone_with_owning_user():
    foreign_key = next(iter(daily_brief_timezones.c.user_id.foreign_keys))
    assert foreign_key.target_fullname == "users.user_id"
    assert foreign_key.ondelete == "CASCADE"
    migration = (
        ROOT / "migrations/versions/20260904_04_daily_brief_timezones.py"
    ).read_text(encoding="utf-8")
    assert 'down_revision = "20260904_03"' in migration
    assert 'op.create_table(\n        "daily_brief_timezones"' in migration


def test_windows_install_includes_iana_timezone_database():
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"tzdata>=2025.2,<2027; platform_system == \'Windows\'"' in project
