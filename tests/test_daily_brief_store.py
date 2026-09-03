"""Persisted cache, concurrency and token fencing using a real SQL database."""

import ast
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)


def load(path, **dependencies):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom)
        and (node.module or "").startswith(("performancelab", "alembic"))
    )]
    scope = {"__name__": __name__, **dependencies}
    exec(compile(tree, path, "exec"), scope)
    return scope


# Load the actual dataclass without importing optional app/provider packages.
tree = ast.parse((ROOT / "performancelab/coaching/daily_brief_policy.py").read_text(encoding="utf-8"))
node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "DailyBriefKey")
scope = dict(dataclass=dataclass, date=date, CONTEXT_VERSION="daily-brief-context-v1")
exec(compile(ast.Module(body=[node], type_ignores=[]), "key", "exec"), scope)
Key = scope["DailyBriefKey"]
SCHEMA = load("performancelab/storage/postgresql_schema.py")
TABLE = SCHEMA["daily_briefs"]
MODULE = load("performancelab/storage/daily_brief_store.py", daily_briefs=TABLE, DailyBriefKey=Key)
Store = MODULE["DailyBriefStore"]


def key(digest="context-a", athlete="athlete-a"):
    return Key(athlete, date(2026, 9, 4), "UTC", digest)


@pytest.fixture
def engine(tmp_path):
    engine = create_engine("sqlite:///" + str(tmp_path / "briefs.sqlite"),
                           connect_args={"timeout": 10})
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    with engine.begin() as connection:
        # Minimal parent keys isolate this table while enforcing its real FKs.
        connection.execute(text("CREATE TABLE users (user_id VARCHAR(36) PRIMARY KEY)"))
        connection.execute(text("CREATE TABLE athletes (athlete_id VARCHAR(36) PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users VALUES ('user-a'), ('user-b')"))
        connection.execute(text("INSERT INTO athletes VALUES ('athlete-a'), ('athlete-b')"))
        TABLE.create(connection)
    yield engine
    engine.dispose()


def reserve(store, **kwargs):
    return store.reserve(user_id="user-a", key=kwargs.pop("key", key()),
                         now=kwargs.pop("now", NOW), **kwargs)


def test_only_one_concurrent_reservation_succeeds(engine):
    barrier = Barrier(2)
    def attempt():
        barrier.wait()
        return reserve(Store(engine))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: attempt(), range(2)))
    assert sum(result is not None for result in results) == 1


def test_completed_brief_survives_new_connection_and_is_not_regenerated(engine):
    store = Store(engine)
    lease = reserve(store)
    assert store.complete(lease, narrative="Daily guidance", reason="first_brief", now=NOW)
    reopened = Store(engine)
    assert reopened.get(user_id="user-a", key=key())["narrative"] == "Daily guidance"
    assert reserve(reopened) is None
    assert not store.complete(lease, narrative="Duplicate", reason="first_brief", now=NOW)


def test_context_change_requires_new_reservation_and_never_returns_stale_as_current(engine):
    store = Store(engine)
    lease = reserve(store)
    store.complete(lease, narrative="Old guidance", reason="first_brief", now=NOW)
    changed = key("new-context")
    assert store.get(user_id="user-a", key=changed) is None
    assert reserve(store, key=changed) is not None


def test_live_lease_blocks_even_a_changed_context(engine):
    store = Store(engine)
    assert reserve(store) is not None
    assert reserve(store, key=key("changed")) is None


def test_expired_worker_cannot_overwrite_replacement(engine):
    store = Store(engine)
    old = reserve(store, lease_duration=timedelta(seconds=10))
    later = NOW + timedelta(seconds=11)
    new = reserve(store, now=later)
    assert new.token != old.token
    assert not store.complete(old, narrative="Late", reason="old", now=later)
    assert store.complete(new, narrative="Current", reason="retry", now=later)
    assert store.get(user_id="user-a", key=key())["narrative"] == "Current"


def test_backoff_survives_reopen_and_applies_to_changed_context(engine):
    store = Store(engine)
    lease = reserve(store)
    assert store.fail(lease, now=NOW, retry_after=NOW + timedelta(minutes=10))
    assert reserve(Store(engine), key=key("changed")) is None
    assert reserve(Store(engine), now=NOW + timedelta(minutes=10)) is not None


def test_withdrawal_cancels_token_and_preserves_saved_content(engine):
    store = Store(engine)
    old = reserve(store)
    store.complete(old, narrative="Saved", reason="first_brief", now=NOW)
    pending = reserve(store, key=key("new"))
    store.cancel_for_user("user-a")
    assert not store.complete(pending, narrative="Blocked", reason="new", now=NOW)
    assert store.export_for_user("user-a")[0]["narrative"] == "Saved"


def test_user_isolation_and_export_excludes_tokens(engine):
    store = Store(engine)
    lease = reserve(store)
    store.complete(lease, narrative="Private", reason="first_brief", now=NOW)
    assert store.get(user_id="user-b", key=key()) is None
    assert store.export_for_user("user-b") == []
    exported = store.export_for_user("user-a")
    assert lease.token not in str(exported)
    assert "lease_token" not in str(exported)


def test_delete_prevents_late_completion_without_touching_other_user(engine):
    store = Store(engine)
    a = reserve(store)
    b = store.reserve(user_id="user-b", key=key(athlete="athlete-b"), now=NOW)
    store.delete_for_user("user-a")
    assert not store.complete(a, narrative="Late", reason="old", now=NOW)
    assert store.complete(b, narrative="Other user", reason="first_brief", now=NOW)


def test_owner_deletion_cascades(engine):
    store = Store(engine)
    lease = reserve(store)
    store.complete(lease, narrative="Saved", reason="first_brief", now=NOW)
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM users WHERE user_id='user-a'"))
    assert store.export_for_user("user-a") == []


def test_invalid_timestamp_and_non_positive_lease_rejected(engine):
    store = Store(engine)
    with pytest.raises(ValueError):
        reserve(store, now=NOW.replace(tzinfo=None))
    with pytest.raises(ValueError):
        reserve(store, lease_duration=timedelta())


def test_migration_matches_shared_schema_and_compiles_for_postgresql():
    class Operations:
        def create_table(self, name, *items):
            self.name, self.items = name, items
    op = Operations()
    migration = load("migrations/versions/20260904_01_create_daily_briefs.py", op=op)
    assert migration["down_revision"] == "20260825_02"
    migration["upgrade"]()
    columns = [item for item in op.items if hasattr(item, "type")]
    assert op.name == TABLE.name
    assert [column.name for column in columns] == list(TABLE.c.keys())
    for migrated, declared in zip(columns, TABLE.columns):
        assert str(migrated.type) == str(declared.type)
        assert migrated.nullable == declared.nullable
    ddl = str(CreateTable(TABLE).compile(dialect=postgresql.dialect()))
    assert "ON DELETE CASCADE" in ddl
    assert "saved_payload JSON" in ddl
