from pathlib import Path

from app.components.daily_brief_timezone import (
    COMMON_TIMEZONES,
    timezone_options,
)


ROOT = Path(__file__).resolve().parents[1]


def test_common_portuguese_timezones_are_available():
    assert "Europe/Lisbon" in COMMON_TIMEZONES
    assert "Atlantic/Azores" in COMMON_TIMEZONES


def test_saved_non_common_timezone_remains_selectable():
    options = timezone_options("Asia/Tokyo")
    assert options[0] == "Asia/Tokyo"
    assert len(options) == len(set(options))


def test_settings_requires_explicit_confirmation_callback():
    source = (ROOT / "app/components/daily_brief_timezone.py").read_text()
    assert "PerformanceLab does not infer it from your device" in source
    assert "on_confirm(selected)" in source


def test_runtime_uses_authenticated_user_for_confirmation():
    source = (ROOT / "app/app.py").read_text()
    assert "daily_brief_timezone_store.confirm(" in source
    assert "user_id=st.session_state.current_user.user_id" in source
