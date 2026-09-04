"""Persist an explicitly confirmed IANA timezone for each user."""

from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Connection

from performancelab.storage.postgresql_schema import daily_brief_timezones


def _user_id(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 36:
        raise ValueError("A user ID of 1 to 36 characters is required")
    return value.strip()


def _timezone_name(value):
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > 64:
        raise ValueError("A timezone name of 1 to 64 characters is required")
    name = value.strip()
    try:
        ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError, OSError):
        raise ValueError("A valid IANA timezone is required") from None
    return name


def _confirmed_at(value):
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError("A timezone-aware confirmation time is required")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class DailyBriefTimezone:
    user_id: str
    timezone_name: str
    confirmed_at: datetime

    def __post_init__(self):
        object.__setattr__(self, "user_id", _user_id(self.user_id))
        object.__setattr__(self, "timezone_name", _timezone_name(self.timezone_name))
        object.__setattr__(self, "confirmed_at", _confirmed_at(self.confirmed_at))


class DailyBriefTimezoneStore:
    def __init__(self, connection: Connection):
        if not isinstance(connection, Connection):
            raise TypeError("A SQLAlchemy Connection is required")
        self.connection = connection

    def get(self, *, user_id):
        row = self.connection.execute(
            select(daily_brief_timezones).where(
                daily_brief_timezones.c.user_id == _user_id(user_id)
            )
        ).mappings().one_or_none()
        if row is None:
            return None
        value = row["confirmed_at"]
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return DailyBriefTimezone(
            user_id=row["user_id"],
            timezone_name=row["timezone_name"],
            confirmed_at=value,
        )

    def confirm(self, *, user_id, timezone_name, confirmed_at):
        value = DailyBriefTimezone(user_id, timezone_name, confirmed_at)
        existing = self.get(user_id=value.user_id)
        if existing == value:
            return value
        if existing is not None:
            self.connection.execute(
                delete(daily_brief_timezones).where(
                    daily_brief_timezones.c.user_id == value.user_id
                )
            )
        self.connection.execute(insert(daily_brief_timezones).values(
            user_id=value.user_id,
            timezone_name=value.timezone_name,
            confirmed_at=value.confirmed_at,
        ))
        return value

    def delete(self, *, user_id):
        self.connection.execute(
            delete(daily_brief_timezones).where(
                daily_brief_timezones.c.user_id == _user_id(user_id)
            )
        )
