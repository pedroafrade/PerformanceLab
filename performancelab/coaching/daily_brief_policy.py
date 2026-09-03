"""Pure scheduling rules for the future automatic Daily Brief coordinator.

No provider calls, persistence or UI side effects. A GENERATE decision is only
eligibility: the coordinator must still atomically reserve the request, enforce
quotas and recheck consent before sending. This module is not wired to login.
"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Mapping, Sequence
from zoneinfo import ZoneInfo

from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
    TrainingCoachConsent,
)


CONTEXT_VERSION = "daily-brief-context-v1"
CONSENT_VERSION = TRAINING_COACH_CONSENT_VERSION


def active_consent_version(
    *, consent: TrainingCoachConsent | None, user_id: str,
) -> str | None:
    """Resolve authorization from an active record belonging to this user.

    The caller must obtain user_id from authenticated identity and the record
    from persistent storage; this function does not perform either operation.
    """
    if (
        isinstance(consent, TrainingCoachConsent)
        and isinstance(user_id, str)
        and consent.user_id == user_id.strip()
        and consent.permits_current_policy()
    ):
        return consent.policy_version
    return None


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Daily Brief requires timezone-aware timestamps")
    return value


def context_fingerprint(
    *,
    plan: Mapping,
    profile: Mapping,
    activities: Sequence[Mapping],
    reports: Sequence[Mapping],
) -> str:
    """Hash minimal, JSON-compatible domain projections, not athlete objects.

    The future adapter must supply only relevant plan/profile facts and dated
    activity/report facts. Exclude wall-clock recovery, login times, UI state,
    credentials and original files. Report dates remain relevant facts.
    Sorting collections makes reordering an identical import a no-op; duplicate
    records are NOT removed here (their resolution belongs to the domain).
    """
    def canonical(value):
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        )

    payload = {
        "version": CONTEXT_VERSION,
        "plan": plan,
        "profile": profile,
        "activities": sorted(activities, key=canonical),
        "reports": sorted(reports, key=canonical),
    }
    return sha256(canonical(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DailyBriefKey:
    athlete_id: str
    local_day: date
    timezone_name: str
    context_digest: str
    context_version: str = CONTEXT_VERSION


def daily_brief_key(
    *, athlete_id: str, now: datetime, timezone_name: str, context_digest: str,
) -> DailyBriefKey:
    if not athlete_id.strip() or not context_digest.strip():
        raise ValueError("An athlete identity and context digest are required")
    # Invalid/missing IANA zones fail explicitly, never fall back to server time.
    local_day = _aware(now).astimezone(ZoneInfo(timezone_name)).date()
    return DailyBriefKey(athlete_id, local_day, timezone_name, context_digest)


class BriefAction(str, Enum):
    BLOCK = "block"
    REUSE = "reuse"
    GENERATE = "generate"
    WAIT = "wait"


@dataclass(frozen=True)
class BriefDecision:
    action: BriefAction
    reason: str


def decide_daily_brief(
    *,
    requested: DailyBriefKey,
    now: datetime,
    enabled: bool = False,
    consent_version: str | None = None,
    saved: DailyBriefKey | None = None,
    retry_not_before: datetime | None = None,
) -> BriefDecision:
    """Choose eligibility using a successfully saved key and athlete-level backoff.

    Read saved/backoff state from the authenticated athlete's persistent store.
    A saved key means a complete successful record, never a failed attempt.
    Require the current combined Training Coach consent. Legacy manual-only
    consent cannot authorize this automatic workflow. The coordinator must
    obtain the version from an ACTIVE stored record, never from the constant.
    """
    _aware(now)
    if not enabled:
        return BriefDecision(BriefAction.BLOCK, "feature_disabled")
    if consent_version != CONSENT_VERSION:
        return BriefDecision(BriefAction.BLOCK, "automatic_consent_required")
    if saved is not None and saved.athlete_id != requested.athlete_id:
        return BriefDecision(BriefAction.BLOCK, "athlete_mismatch")
    if saved == requested:
        return BriefDecision(BriefAction.REUSE, "unchanged")
    if retry_not_before is not None and _aware(now) < _aware(retry_not_before):
        return BriefDecision(BriefAction.WAIT, "retry_backoff")
    if saved is None:
        reason = "first_brief"
    elif saved.local_day != requested.local_day:
        reason = "new_local_day"
    elif saved.timezone_name != requested.timezone_name:
        reason = "timezone_changed"
    elif saved.context_version != requested.context_version:
        reason = "context_version_changed"
    else:
        reason = "relevant_context_changed"
    return BriefDecision(BriefAction.GENERATE, reason)
