"""Daily Brief privacy operations on the application's shared connection.

Unlike generation leases, these operations must participate in account deletion
and consent-withdrawal transactions. This class never commits or rolls back.
It creates no tables. Before the Daily Brief migration there is nothing to
export/cancel/delete; a missing table is handled explicitly, not a SQL error.
Database permission/connection errors are not swallowed.
"""

from sqlalchemy import delete, inspect, select, update
from datetime import timezone
from sqlalchemy.engine import Connection

from performancelab.storage.postgresql_schema import daily_briefs, training_coach_quota_reservations


def _identity(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 36:
        raise ValueError("A non-empty internal identity of at most 36 characters is required")
    return value.strip()


def _utc_timestamp(value):
    # SQLite returns naive SQL timestamps although these records are stored UTC.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


class DailyBriefPrivacyRepository:
    def __init__(self, connection: Connection):
        if not isinstance(connection, Connection):
            raise TypeError("A shared SQLAlchemy Connection is required")
        self._connection = connection

    def _exists(self, table=daily_briefs):
        # Do not cache this result: migrations may run between app sessions.
        return inspect(self._connection).has_table(table.name, schema=table.schema)

    def export_quota_for_user(self, user_id: str) -> list[dict]:
        user_id = _identity(user_id)
        table = training_coach_quota_reservations
        if not self._exists(table):
            return []
        rows = self._connection.execute(select(table).where(table.c.user_id == user_id)
                                        .order_by(table.c.reserved_at, table.c.request_id)).mappings()
        return [{"request_id": row["request_id"], "purpose": row["purpose"],
                 "state": row["state"], "utc_day": row["utc_day"].isoformat(),
                 "reserved_at": _utc_timestamp(row["reserved_at"]),
                 "expires_at": _utc_timestamp(row["expires_at"])} for row in rows]

    def export_for_user(self, user_id: str, *, athlete_id: str) -> list[dict]:
        user_id, athlete_id = _identity(user_id), _identity(athlete_id)
        if not self._exists():
            return []
        rows = self._connection.execute(select(daily_briefs.c.saved_payload).where(
            daily_briefs.c.user_id == user_id,
            daily_briefs.c.athlete_id == athlete_id,
            daily_briefs.c.saved_key.is_not(None),
            daily_briefs.c.saved_payload.is_not(None),
        )).scalars().all()
        # Explicit export fields exclude internal reservation/retry state.
        return [{field: row.get(field) for field in
                 ("key", "narrative", "generated_at", "reason")} for row in rows]

    def cancel_for_user(self, user_id: str) -> None:
        user_id = _identity(user_id)
        if self._exists():
            self._connection.execute(update(daily_briefs).where(
                daily_briefs.c.user_id == user_id,
            ).values(lease_key=None, lease_token=None, lease_until=None))

    def delete_for_user(self, user_id: str) -> None:
        user_id = _identity(user_id)
        table = training_coach_quota_reservations
        if self._exists(table):
            self._connection.execute(delete(table).where(table.c.user_id == user_id))
        if self._exists():
            self._connection.execute(delete(daily_briefs).where(
                daily_briefs.c.user_id == user_id,
            ))
