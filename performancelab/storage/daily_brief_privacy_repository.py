"""Daily Brief privacy operations on the application's shared connection.

Unlike generation leases, these operations must participate in account deletion
and consent-withdrawal transactions. This class never commits or rolls back.
It creates no tables. Before the Daily Brief migration there is nothing to
export/cancel/delete; a missing table is handled explicitly, not a SQL error.
Database permission/connection errors are not swallowed.
"""

from sqlalchemy import delete, inspect, select, update
from sqlalchemy.engine import Connection

from performancelab.storage.postgresql_schema import daily_briefs


def _identity(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 36:
        raise ValueError("A non-empty internal identity of at most 36 characters is required")
    return value.strip()


class DailyBriefPrivacyRepository:
    def __init__(self, connection: Connection):
        if not isinstance(connection, Connection):
            raise TypeError("A shared SQLAlchemy Connection is required")
        self._connection = connection

    def _exists(self):
        # Do not cache this result: migrations may run between app sessions.
        return inspect(self._connection).has_table(daily_briefs.name,
                                                  schema=daily_briefs.schema)

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
        if self._exists():
            self._connection.execute(delete(daily_briefs).where(
                daily_briefs.c.user_id == user_id,
            ))
