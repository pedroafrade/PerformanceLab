"""Shared quota concurrency, recovery, UTC boundaries and privacy contracts."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import io
from pathlib import Path
from runpy import run_path
from threading import Barrier

import pytest
from sqlalchemy import create_engine, event, insert, select, text
from sqlalchemy.exc import IntegrityError

from performancelab.storage.postgresql_schema import (
    daily_briefs, metadata, training_coach_quota_reservations as reservations, training_coach_usage,
)
from performancelab.storage.training_coach_quota_store import TrainingCoachQuotaStore
from performancelab.storage.daily_brief_privacy_repository import DailyBriefPrivacyRepository
from performancelab.training_coach_usage_limits import TrainingCoachUsageLimits


NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)
LIMIT = TrainingCoachUsageLimits(1, 1)
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def engine(tmp_path):
    engine = create_engine("sqlite:///" + str(tmp_path / "quota.sqlite"),
                           connect_args={"timeout": 10})
    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE users (user_id VARCHAR(36) PRIMARY KEY)"))
        connection.execute(text("INSERT INTO users VALUES ('user-a'), ('user-b')"))
        training_coach_usage.create(connection)
        reservations.create(connection)
    yield engine
    engine.dispose()


def reserve(store, request_id="request-a", user_id="user-a", purpose="activity", now=NOW, limits=LIMIT):
    return store.reserve(user_id=user_id, request_id=request_id, purpose=purpose, limits=limits, now=now)


def usage(engine, request_id, *, user_id="user-a", now=NOW, status="generated"):
    with engine.begin() as connection:
        connection.execute(insert(training_coach_usage).values(
            usage_id=request_id, user_id=user_id, occurred_at=now, status=status,
        ))


def test_two_purposes_share_one_atomic_global_limit(engine):
    barrier = Barrier(2)
    def attempt(item):
        barrier.wait()
        return reserve(TrainingCoachQuotaStore(engine), request_id="request-" + str(item),
                       user_id="user-a" if item == 0 else "user-b",
                       purpose="activity" if item == 0 else "daily_brief")
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, range(2)))
    assert sum(row.permitted for row in results) == 1
    assert next(row for row in results if not row.permitted).reason == "global_daily_limit"


def test_separate_store_instances_share_user_limit(engine):
    limits = TrainingCoachUsageLimits(1, 10)
    assert reserve(TrainingCoachQuotaStore(engine), limits=limits).permitted
    denied = reserve(TrainingCoachQuotaStore(engine), "other", purpose="daily_brief", limits=limits)
    assert not denied.permitted and denied.reason == "user_daily_limit"


def test_duplicate_request_never_authorises_another_call(engine):
    store = TrainingCoachQuotaStore(engine)
    first = reserve(store)
    second = reserve(store)
    assert first.permitted
    assert not second.permitted and second.reservation is None
    assert second.reason == "request_already_recorded"


def test_recorded_success_and_reservation_are_not_double_counted(engine):
    store = TrainingCoachQuotaStore(engine)
    limits = TrainingCoachUsageLimits(2, 2)
    receipt = reserve(store, limits=limits).reservation
    usage(engine, receipt.request_id)
    assert store.finish(receipt, outcome="generated", now=NOW)
    assert store.finish(receipt, outcome="generated", now=NOW)
    second = reserve(store, "second", limits=limits)
    assert second.permitted and second.remaining_global_requests == 0
    assert not reserve(store, "third", limits=limits).permitted


def test_legacy_success_counts_but_failed_usage_does_not(engine):
    store = TrainingCoachQuotaStore(engine)
    usage(engine, "failed", status="failed")
    usage(engine, "legacy")
    assert not reserve(store).permitted
    assert reserve(store, "tomorrow", now=NOW + timedelta(days=1)).permitted


def test_confirmed_failure_releases_once_but_id_cannot_be_reused(engine):
    store = TrainingCoachQuotaStore(engine)
    receipt = reserve(store).reservation
    assert store.finish(receipt, outcome="not_generated", now=NOW)
    assert store.finish(receipt, outcome="not_generated", now=NOW)
    assert not store.finish(receipt, outcome="generated", now=NOW)
    assert not reserve(store).permitted
    assert reserve(store, "retry").permitted


def test_expiry_is_not_permission_to_repeat_uncertain_request(engine):
    store = TrainingCoachQuotaStore(engine)
    receipt = reserve(store).reservation
    later = NOW + timedelta(minutes=6)
    assert not store.finish(receipt, outcome="not_generated", now=later)
    assert not reserve(store, "retry", now=later).permitted
    assert store.finish(receipt, outcome="generated", now=later)


def test_success_already_logged_cannot_be_released(engine):
    store = TrainingCoachQuotaStore(engine)
    receipt = reserve(store).reservation
    usage(engine, receipt.request_id)
    assert not store.finish(receipt, outcome="not_generated", now=NOW)
    assert not reserve(store, "retry").permitted


def test_unexpected_success_after_release_still_counts(engine):
    store = TrainingCoachQuotaStore(engine)
    receipt = reserve(store).reservation
    assert store.finish(receipt, outcome="not_generated", now=NOW)
    usage(engine, receipt.request_id)
    assert not reserve(store, "retry").permitted


def test_midnight_result_belongs_to_original_admission_day(engine):
    store = TrainingCoachQuotaStore(engine)
    before = NOW.replace(hour=23, minute=59)
    after = before + timedelta(minutes=2)
    receipt = reserve(store, now=before).reservation
    usage(engine, receipt.request_id, now=after)
    assert store.finish(receipt, outcome="generated", now=after)
    assert reserve(store, "new-day", now=after).permitted


def test_quota_day_is_utc_not_callers_offset(engine):
    store = TrainingCoachQuotaStore(engine)
    shifted = datetime(2026, 9, 5, 0, 30, tzinfo=timezone(timedelta(hours=2)))
    assert reserve(store, now=shifted).permitted
    assert not reserve(store, "again", now=shifted.astimezone(timezone.utc)).permitted
    with engine.connect() as connection:
        assert connection.execute(select(reservations.c.utc_day)).scalar_one().isoformat() == "2026-09-04"


def test_foreign_or_modified_receipt_cannot_release_budget(engine):
    store = TrainingCoachQuotaStore(engine)
    receipt = reserve(store).reservation
    assert not store.finish(replace(receipt, user_id="user-b"), outcome="not_generated", now=NOW)
    assert not store.finish(replace(receipt, expires_at=NOW), outcome="not_generated", now=NOW)


def test_reservation_failure_rolls_back_without_spending_capacity(engine):
    store = TrainingCoachQuotaStore(engine)
    with pytest.raises(IntegrityError):
        reserve(store, user_id="missing-user")
    assert reserve(store).permitted


def test_privacy_export_delete_and_rollback(engine):
    store = TrainingCoachQuotaStore(engine)
    limits = TrainingCoachUsageLimits(1, 2)
    receipt = reserve(store, limits=limits).reservation
    reserve(store, "other", user_id="user-b", purpose="daily_brief", limits=limits)
    with pytest.raises(RuntimeError):
        with engine.begin() as connection:
            privacy = DailyBriefPrivacyRepository(connection)
            rows = privacy.export_quota_for_user("user-a")
            assert len(rows) == 1 and rows[0]["request_id"] == receipt.request_id
            assert rows[0]["reserved_at"].endswith("+00:00")
            assert set(rows[0]) == {"request_id", "purpose", "state", "utc_day", "reserved_at", "expires_at"}
            privacy.delete_for_user("user-a")
            raise RuntimeError("rollback")
    with engine.begin() as connection:
        privacy = DailyBriefPrivacyRepository(connection)
        assert len(privacy.export_quota_for_user("user-a")) == 1
        privacy.delete_for_user("user-a")
        assert privacy.export_quota_for_user("user-a") == []
        assert len(privacy.export_quota_for_user("user-b")) == 1
    assert not store.finish(receipt, outcome="generated", now=NOW)


def test_owner_deletion_cascades(engine):
    reserve(TrainingCoachQuotaStore(engine))
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM users WHERE user_id = 'user-a'"))
        assert connection.execute(select(reservations.c.request_id)).all() == []


def test_missing_migration_fails_closed_without_creating_tables():
    engine = create_engine("sqlite://")
    try:
        with pytest.raises(Exception):
            reserve(TrainingCoachQuotaStore(engine))
        with engine.begin() as connection:
            assert DailyBriefPrivacyRepository(connection).export_quota_for_user("user-a") == []
            assert connection.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).all() == []
    finally:
        engine.dispose()


def test_postgresql_migration_sql_is_consistent_with_metadata():
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    module = run_path(str(ROOT / "migrations/versions/20260904_03_training_coach_quota.py"))
    assert module["down_revision"] == "20260904_02"
    output = io.StringIO()
    context = MigrationContext.configure(dialect_name="postgresql", opts={
        "as_sql": True, "output_buffer": output, "target_metadata": metadata,
    })
    with Operations.context(context):
        module["upgrade"]()
    sql = output.getvalue()
    assert "ON DELETE CASCADE" in sql
    for constraint in reservations.constraints:
        assert str(constraint.name) in sql
    assert "ck_training_coach_quota_reservations_ck_" not in sql


@pytest.mark.parametrize("arguments", [
    {"user_id": ""}, {"request_id": "x" * 37}, {"purpose": "other"},
    {"now": datetime(2026, 9, 4)}, {"limits": None},
])
def test_invalid_admissions_do_not_spend_budget(engine, arguments):
    store = TrainingCoachQuotaStore(engine)
    with pytest.raises((ValueError, TypeError)):
        reserve(store, **arguments)
    assert reserve(store).permitted
