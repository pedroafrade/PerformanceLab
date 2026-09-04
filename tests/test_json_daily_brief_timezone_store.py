from datetime import datetime, timezone

import pytest

from performancelab.storage.json_daily_brief_timezone_store import (
    JsonDailyBriefTimezoneStore,
)


NOW = datetime(2026, 9, 4, 11, tzinfo=timezone.utc)


def test_local_timezone_round_trip_survives_new_store_instance(tmp_path):
    first = JsonDailyBriefTimezoneStore(tmp_path)
    first.confirm(
        user_id="user-1",
        timezone_name="Europe/Lisbon",
        confirmed_at=NOW,
    )

    saved = JsonDailyBriefTimezoneStore(tmp_path).get(user_id="user-1")
    assert saved.timezone_name == "Europe/Lisbon"
    assert saved.confirmed_at == NOW


def test_invalid_timezone_does_not_replace_local_preference(tmp_path):
    store = JsonDailyBriefTimezoneStore(tmp_path)
    store.confirm(
        user_id="user-1",
        timezone_name="Europe/Lisbon",
        confirmed_at=NOW,
    )

    with pytest.raises(ValueError):
        store.confirm(
            user_id="user-1",
            timezone_name="Invalid/Timezone",
            confirmed_at=NOW,
        )

    assert store.get(user_id="user-1").timezone_name == "Europe/Lisbon"


def test_missing_and_deleted_local_preferences_return_none(tmp_path):
    store = JsonDailyBriefTimezoneStore(tmp_path)
    assert store.get(user_id="user-1") is None
    store.confirm(
        user_id="user-1",
        timezone_name="Atlantic/Azores",
        confirmed_at=NOW,
    )
    store.delete(user_id="user-1")
    assert store.get(user_id="user-1") is None
