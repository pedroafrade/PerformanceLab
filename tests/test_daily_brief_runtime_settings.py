import pytest

from performancelab.daily_brief_runtime_settings import (
    DAILY_BRIEF_SETTING_NAMES,
    DailyBriefRuntimeSettings,
)


def test_daily_brief_is_disabled_by_default():
    settings = DailyBriefRuntimeSettings.from_mapping({})

    assert settings.enabled is False
    assert settings.allowed_user_ids == frozenset()
    assert settings.permits("user-1") is False


def test_enabled_rollout_requires_and_enforces_explicit_users():
    settings = DailyBriefRuntimeSettings.from_mapping({
        "DAILY_BRIEF_ENABLED": "true",
        "DAILY_BRIEF_ALLOWED_USER_IDS": "user-1, user-2",
    })

    assert settings.permits("user-1") is True
    assert settings.permits("user-2") is True
    assert settings.permits("user-3") is False


@pytest.mark.parametrize(
    "values",
    (
        {"DAILY_BRIEF_ENABLED": "sometimes"},
        {"DAILY_BRIEF_ENABLED": True},
        {
            "DAILY_BRIEF_ENABLED": True,
            "DAILY_BRIEF_ALLOWED_USER_IDS": "*",
        },
        {
            "DAILY_BRIEF_ENABLED": True,
            "DAILY_BRIEF_ALLOWED_USER_IDS": "user-1,",
        },
    ),
)
def test_invalid_or_broad_rollout_fails_closed(values):
    with pytest.raises((TypeError, ValueError)):
        DailyBriefRuntimeSettings.from_mapping(values)


def test_disabled_configuration_may_keep_future_allowlist():
    settings = DailyBriefRuntimeSettings.from_mapping({
        "DAILY_BRIEF_ENABLED": False,
        "DAILY_BRIEF_ALLOWED_USER_IDS": "user-1",
    })

    assert settings.permits("user-1") is False


def test_allowlist_is_not_exposed_by_generated_representation():
    settings = DailyBriefRuntimeSettings.from_mapping({
        "DAILY_BRIEF_ENABLED": True,
        "DAILY_BRIEF_ALLOWED_USER_IDS": "private-user-id",
    })

    assert "private-user-id" not in repr(settings)


def test_setting_names_are_explicit_for_environment_and_secrets_loading():
    assert DAILY_BRIEF_SETTING_NAMES == (
        "DAILY_BRIEF_ENABLED",
        "DAILY_BRIEF_ALLOWED_USER_IDS",
    )
