"""Local JSON persistence for explicitly confirmed Daily Brief timezones."""

import json
from datetime import datetime
from pathlib import Path

from performancelab.storage.daily_brief_timezone_store import (
    DailyBriefTimezone,
)


class JsonDailyBriefTimezoneStore:
    """Store one versioned timezone preference per local user."""

    def __init__(self, directory: str | Path = "data/daily_brief_timezones"):
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

    def _path_for(self, user_id: str) -> Path:
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("A user ID is required")
        normalized = user_id.strip()
        if len(normalized) > 36 or Path(normalized).name != normalized:
            raise ValueError("A valid user ID is required")
        return self._directory / f"{normalized}.json"

    def get(self, *, user_id):
        path = self._path_for(user_id)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        if data.get("version") != 1:
            raise ValueError("Unsupported Daily Brief timezone version")
        return DailyBriefTimezone(
            user_id=data["user_id"],
            timezone_name=data["timezone_name"],
            confirmed_at=datetime.fromisoformat(data["confirmed_at"]),
        )

    def confirm(self, *, user_id, timezone_name, confirmed_at):
        value = DailyBriefTimezone(user_id, timezone_name, confirmed_at)
        path = self._path_for(value.user_id)
        temporary_path = path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as stream:
            json.dump(
                {
                    "version": 1,
                    "user_id": value.user_id,
                    "timezone_name": value.timezone_name,
                    "confirmed_at": value.confirmed_at.isoformat(),
                },
                stream,
                indent=4,
                ensure_ascii=False,
            )
        temporary_path.replace(path)
        return value

    def delete(self, *, user_id):
        path = self._path_for(user_id)
        if path.exists():
            path.unlink()
