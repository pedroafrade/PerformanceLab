"""Fail-closed rollout settings for automatic Daily Brief generation."""

from collections.abc import Mapping
from dataclasses import dataclass, field


DAILY_BRIEF_SETTING_NAMES = (
    "DAILY_BRIEF_ENABLED",
    "DAILY_BRIEF_ALLOWED_USER_IDS",
)


def _enabled(value):
    if isinstance(value, bool):
        return value
    if not isinstance(value, str):
        raise TypeError("DAILY_BRIEF_ENABLED must be true or false")
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError("DAILY_BRIEF_ENABLED must be true or false")


def _allowed_users(value):
    if value is None:
        return frozenset()
    if not isinstance(value, str):
        raise TypeError("DAILY_BRIEF_ALLOWED_USER_IDS must be a string")
    values = [item.strip() for item in value.split(",")]
    if any(not item or len(item) > 36 for item in values):
        raise ValueError("Daily Brief user IDs must contain 1 to 36 characters")
    if "*" in values:
        raise ValueError("Daily Brief rollout does not accept a wildcard")
    return frozenset(values)


@dataclass(frozen=True)
class DailyBriefRuntimeSettings:
    """Explicit kill switch plus a narrow user allowlist."""

    enabled: bool = False
    allowed_user_ids: frozenset[str] = field(
        default_factory=frozenset,
        repr=False,
    )

    def __post_init__(self):
        enabled = _enabled(self.enabled)
        allowed = self.allowed_user_ids
        if not isinstance(allowed, frozenset):
            raise TypeError("allowed_user_ids must be a frozenset")
        if enabled and not allowed:
            raise ValueError("An enabled Daily Brief rollout requires allowed users")
        for user_id in allowed:
            if not isinstance(user_id, str) or not user_id or len(user_id) > 36:
                raise ValueError("Invalid Daily Brief rollout user ID")
        object.__setattr__(self, "enabled", enabled)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]):
        if not isinstance(values, Mapping):
            raise TypeError("Daily Brief settings require a mapping")
        enabled = _enabled(values.get("DAILY_BRIEF_ENABLED", False))
        allowed = _allowed_users(values.get("DAILY_BRIEF_ALLOWED_USER_IDS"))
        return cls(enabled=enabled, allowed_user_ids=allowed)

    def permits(self, user_id: str) -> bool:
        if not isinstance(user_id, str):
            return False
        return self.enabled and user_id.strip() in self.allowed_user_ids


def load_daily_brief_runtime_settings(values: Mapping[str, object]):
    """Fail closed when deployment values are absent or malformed."""

    try:
        return DailyBriefRuntimeSettings.from_mapping(values)
    except (TypeError, ValueError):
        return DailyBriefRuntimeSettings()
