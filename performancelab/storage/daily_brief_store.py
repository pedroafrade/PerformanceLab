"""SQL storage primitives for Daily Brief, not yet connected to the app.

Supports PostgreSQL and SQLite. Every operation owns a short transaction on an
Engine (not the app's shared Connection). Never hold a transaction across a
provider call. Production schema is installed by Alembic, not by this class.
Authorization, consent and quotas must be checked by the future coordinator.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from uuid import uuid4

from sqlalchemy import delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from performancelab.coaching.daily_brief_policy import DailyBriefKey
from performancelab.storage.postgresql_schema import daily_briefs


def _now(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("An aware timestamp is required")
    return value.astimezone(timezone.utc)


def _identity(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 36:
        raise ValueError("A non-empty internal identity of at most 36 characters is required")
    return value.strip()


def _key_data(key):
    values = asdict(key)
    values["local_day"] = key.local_day.isoformat()
    return values


def _request_key(key):
    return sha256(json.dumps(_key_data(key), sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class BriefLease:
    user_id: str
    key: DailyBriefKey
    token: str = field(repr=False)
    expires_at: datetime


class DailyBriefStore:
    """Keep the latest successful brief and at most one valid lease per owner.

    Lease expiry allows recovery after a crashed worker. It cannot guarantee
    exactly-once external billing after an ambiguous network timeout: a future
    coordinator must handle uncertain provider outcomes conservatively.
    """

    def __init__(self, engine: Engine):
        if not isinstance(engine, Engine):
            raise TypeError("DailyBriefStore requires a SQLAlchemy Engine")
        if engine.dialect.name not in {"postgresql", "sqlite"}:
            raise ValueError("Daily Brief storage supports PostgreSQL and SQLite")
        self._engine = engine

    @staticmethod
    def _owner(user_id, athlete_id):
        return (daily_briefs.c.user_id == _identity(user_id)) & (
            daily_briefs.c.athlete_id == _identity(athlete_id)
        )

    def reserve(self, *, user_id: str, key: DailyBriefKey, now: datetime,
                lease_duration: timedelta = timedelta(minutes=5)) -> BriefLease | None:
        """Atomically acquire eligibility; None means cached, busy or in backoff."""
        user_id = _identity(user_id)
        owner = self._owner(user_id, key.athlete_id)
        now = _now(now)
        if not isinstance(lease_duration, timedelta) or lease_duration <= timedelta():
            raise ValueError("lease_duration must be positive")
        expires = now + lease_duration
        token, request_key = str(uuid4()), _request_key(key)
        insert = pg_insert if self._engine.dialect.name == "postgresql" else sqlite_insert
        with self._engine.begin() as connection:
            connection.execute(insert(daily_briefs).values(
                user_id=user_id, athlete_id=_identity(key.athlete_id),
            ).on_conflict_do_nothing(index_elements=["user_id", "athlete_id"]))
            acquired = connection.execute(update(daily_briefs).where(
                owner,
                or_(daily_briefs.c.saved_key.is_(None), daily_briefs.c.saved_key != request_key),
                or_(daily_briefs.c.lease_until.is_(None), daily_briefs.c.lease_until <= now),
                or_(daily_briefs.c.retry_after.is_(None), daily_briefs.c.retry_after <= now),
            ).values(lease_key=request_key, lease_token=token, lease_until=expires))
            if acquired.rowcount != 1:
                return None
        return BriefLease(user_id, key, token, expires)

    def _active_lease(self, lease, now):
        return (
            self._owner(lease.user_id, lease.key.athlete_id)
            & (daily_briefs.c.lease_token == lease.token)
            & (daily_briefs.c.lease_key == _request_key(lease.key))
            & (daily_briefs.c.lease_until > _now(now))
        )

    def complete(self, lease: BriefLease, *, narrative: str, reason: str,
                 now: datetime) -> bool:
        """Commit only a still-valid lease; a late/stale worker cannot overwrite."""
        now = _now(now)
        if not isinstance(narrative, str) or not narrative.strip():
            raise ValueError("A non-empty generated narrative is required")
        if len(narrative) > 30000:
            raise ValueError("Generated narrative exceeds the storage limit")
        if not isinstance(reason, str) or not reason.strip() or len(reason) > 100:
            raise ValueError("A bounded generation reason is required")
        payload = dict(key=_key_data(lease.key), narrative=narrative.strip(),
                       generated_at=now.isoformat(), reason=reason)
        with self._engine.begin() as connection:
            result = connection.execute(update(daily_briefs).where(
                self._active_lease(lease, now),
            ).values(saved_key=_request_key(lease.key), saved_payload=payload,
                     lease_key=None, lease_token=None, lease_until=None, retry_after=None))
            return result.rowcount == 1

    def fail(self, lease: BriefLease, *, now: datetime, retry_after: datetime) -> bool:
        """Release a valid failed request and apply owner-wide retry backoff."""
        now, retry_after = _now(now), _now(retry_after)
        if retry_after <= now:
            raise ValueError("retry_after must be later than now")
        with self._engine.begin() as connection:
            result = connection.execute(update(daily_briefs).where(
                self._active_lease(lease, now),
            ).values(lease_key=None, lease_token=None, lease_until=None,
                     retry_after=retry_after))
            return result.rowcount == 1

    def get(self, *, user_id: str, key: DailyBriefKey) -> dict | None:
        """Return only the exact current key, never label an old brief as current."""
        with self._engine.connect() as connection:
            return connection.execute(select(daily_briefs.c.saved_payload).where(
                self._owner(user_id, key.athlete_id),
                daily_briefs.c.saved_key == _request_key(key),
            )).scalar_one_or_none()

    def cancel_for_user(self, user_id: str) -> None:
        """Invalidate outstanding tokens on withdrawal; keep saved history."""
        with self._engine.begin() as connection:
            connection.execute(update(daily_briefs).where(
                daily_briefs.c.user_id == _identity(user_id),
            ).values(lease_key=None, lease_token=None, lease_until=None))

    def export_for_user(self, user_id: str) -> list[dict]:
        """Export retained content without exposing reservation tokens."""
        with self._engine.connect() as connection:
            values = connection.execute(select(daily_briefs.c.saved_payload).where(
                daily_briefs.c.user_id == _identity(user_id),
                daily_briefs.c.saved_key.is_not(None),
            ).order_by(daily_briefs.c.athlete_id)).scalars().all()
        return list(values)

    def delete_for_user(self, user_id: str) -> None:
        """Delete retained content and reservations; late completions are rejected."""
        with self._engine.begin() as connection:
            connection.execute(delete(daily_briefs).where(
                daily_briefs.c.user_id == _identity(user_id),
            ))
