from pathlib import Path

from performancelab.daily_brief_runtime_settings import (
    DailyBriefRuntimeSettings,
    load_daily_brief_runtime_settings,
)


ROOT = Path(__file__).resolve().parents[1]


def test_invalid_runtime_configuration_fails_closed():
    settings = load_daily_brief_runtime_settings({
        "DAILY_BRIEF_ENABLED": "invalid",
        "DAILY_BRIEF_ALLOWED_USER_IDS": "user-1",
    })
    assert settings == DailyBriefRuntimeSettings()


def test_valid_runtime_configuration_preserves_narrow_rollout():
    settings = load_daily_brief_runtime_settings({
        "DAILY_BRIEF_ENABLED": "true",
        "DAILY_BRIEF_ALLOWED_USER_IDS": "user-1",
    })
    assert settings.permits("user-1") is True
    assert settings.permits("user-2") is False


def test_app_loads_daily_brief_settings_without_triggering_generation():
    source = (ROOT / "app/app.py").read_text(encoding="utf-8")
    assert "*DAILY_BRIEF_SETTING_NAMES" in source
    assert "if daily_brief_runtime_settings.enabled" in source
    assert "daily_brief_generation_service.generate(" not in source
