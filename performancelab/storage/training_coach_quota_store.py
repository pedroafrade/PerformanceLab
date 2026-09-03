"""Shared SQL admission budget for Activities and Daily Brief.

All generation entry points must use this store before enabling the new budget.
It does not authorise an athlete or grant Training Coach consent. Every method
owns a short transaction; never hold its connection during provider work.
Successful usage and reservations share request_id/usage_id to avoid counting
the same request twice. Unknown/expired outcomes stay charged for their UTC day.
"""

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, insert, select, text, union, update
from sqlalchemy.engine import Engine

from performancelab.storage.postgresql_schema import (
    training_coach_quota_reservations as reservations, training_coach_usage,
)
from performancelab.training_coach_usage_limits import TrainingCoachUsageCounts, TrainingCoachUsageLimits


_LOCK_ID = 0x504C544351554F54  # Stable signed bigint, shared across app workers.


def _identity(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 36:
        raise ValueError("An internal identifier of at most 36 characters is required")
    return value.strip()


def _now(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware timestamp is required")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class QuotaReservation:
    request_id: str
    user_id: str
    purpose: str
    reserved_at: datetime
    expires_at: datetime


@dataclass(frozen=True)
class QuotaAdmission:
    permitted: bool
    reason: str | None
    reservation: QuotaReservation | None
    remaining_user_requests: int
    remaining_global_requests: int


class TrainingCoachQuotaStore:
    def __init__(self, engine: Engine):
        if not isinstance(engine, Engine):
            raise TypeError("A SQLAlchemy Engine is required")
        if engine.dialect.name not in ("postgresql", "sqlite"):
            raise ValueError("Quota reservations support PostgreSQL and SQLite")
        self._engine = engine

    @contextmanager
    def _transaction(self):
        with self._engine.connect() as connection:
            try:
                if connection.dialect.name == "sqlite":
                    # Serialize read/check/write across separate connections/processes.
                    connection.exec_driver_sql("BEGIN IMMEDIATE")
                else:
                    connection.begin()
                    connection.execute(text("SELECT pg_advisory_xact_lock(:lock_id)"),
                                       {"lock_id": _LOCK_ID})
                yield connection
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    @staticmethod
    def _counts(connection, user_id, now):
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # UNION (not UNION ALL) deduplicates an outcome persisted in both tables.
        occupied = union(
            select(training_coach_usage.c.usage_id.label("request_id"),
                   training_coach_usage.c.user_id).where(
                training_coach_usage.c.status == "generated",
                training_coach_usage.c.occurred_at >= start,
                training_coach_usage.c.occurred_at < start + timedelta(days=1),
                # A reserved request belongs to its admission day, even if its
                # result is recorded after midnight. Do not charge it twice.
                ~training_coach_usage.c.usage_id.in_(select(reservations.c.request_id).where(
                    reservations.c.state.in_(("reserved", "generated")),
                )),
            ),
            select(reservations.c.request_id, reservations.c.user_id).where(
                reservations.c.utc_day == start.date(),
                reservations.c.state.in_(("reserved", "generated")),
            ),
        ).subquery()
        return TrainingCoachUsageCounts(
            global_count=connection.execute(select(func.count()).select_from(occupied)).scalar_one(),
            user_count=connection.execute(select(func.count()).select_from(occupied).where(
                occupied.c.user_id == user_id)).scalar_one(),
        )

    def reserve(self, *, user_id: str, request_id: str, purpose: str,
                limits: TrainingCoachUsageLimits, now: datetime) -> QuotaAdmission:
        """Admit once; duplicate request IDs never grant another provider call.

        The caller binds a new internal request ID to one generation attempt
        and uses that SAME ID for its TrainingCoachUsageEvent. Failed/uncertain
        acquisitions must not be interpreted as permission to generate.
        """
        user_id, request_id, now = _identity(user_id), _identity(request_id), _now(now)
        if purpose not in ("activity", "daily_brief"):
            raise ValueError("Unsupported quota purpose")
        if not isinstance(limits, TrainingCoachUsageLimits):
            raise TypeError("TrainingCoachUsageLimits are required")
        with self._transaction() as connection:
            counts = self._counts(connection, user_id, now)
            decision = limits.evaluate(counts)
            exists = connection.execute(select(reservations.c.request_id).where(
                reservations.c.request_id == request_id)).scalar_one_or_none()
            old_usage = connection.execute(select(training_coach_usage.c.usage_id).where(
                training_coach_usage.c.usage_id == request_id)).scalar_one_or_none()
            if exists is not None or old_usage is not None or not decision.permitted:
                return QuotaAdmission(False, "request_already_recorded" if
                                      exists is not None or old_usage is not None else decision.reason,
                                      None, decision.remaining_user_requests,
                                      decision.remaining_global_requests)
            receipt = QuotaReservation(request_id, user_id, purpose, now,
                                       now + timedelta(minutes=5))
            connection.execute(insert(reservations).values(
                request_id=request_id, user_id=user_id, purpose=purpose, state="reserved",
                utc_day=now.date(), reserved_at=now, expires_at=receipt.expires_at,
            ))
            return QuotaAdmission(True, None, receipt,
                                  decision.remaining_user_requests - 1,
                                  decision.remaining_global_requests - 1)

    def finish(self, receipt: QuotaReservation, *, outcome: str, now: datetime) -> bool:
        """Mark a known result. Never release an uncertain or expired request.

        outcome='not_generated' is only for a confirmed no-generation result,
        not a timeout or unknown provider failure. A late success may be logged
        as generated but cannot create a fresh allowance. No outcome reopens a
        finished ID; another attempt always needs a new reservation.
        """
        now = _now(now)
        if not isinstance(receipt, QuotaReservation):
            raise TypeError("A quota reservation receipt is required")
        if outcome not in ("generated", "not_generated"):
            raise ValueError("Only confirmed quota outcomes can be finalised")
        target = "generated" if outcome == "generated" else "released"
        owner = ((reservations.c.request_id == receipt.request_id)
                 & (reservations.c.user_id == receipt.user_id)
                 & (reservations.c.purpose == receipt.purpose)
                 & (reservations.c.reserved_at == receipt.reserved_at)
                 & (reservations.c.expires_at == receipt.expires_at))
        with self._transaction() as connection:
            state = connection.execute(select(reservations.c.state).where(owner)).scalar_one_or_none()
            if state == target:
                return True
            if state != "reserved" or now < receipt.reserved_at:
                return False
            if target == "released":
                if now >= receipt.expires_at:
                    return False
                generated = connection.execute(select(training_coach_usage.c.usage_id).where(
                    training_coach_usage.c.usage_id == receipt.request_id,
                    training_coach_usage.c.status == "generated",
                )).scalar_one_or_none()
                if generated is not None:
                    return False
            connection.execute(update(reservations).where(owner).values(state=target))
            return True
