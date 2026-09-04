"""Orchestrate Daily Brief decisions; not connected to login or a provider yet.

The generation adapter receives INTERNAL context. It must minimize that context,
build the provider prompt, enforce output/safety constraints and report usage.
Its request timeout must be shorter than the five-minute lease. Do not pass a
raw SDK/client method as generate. No SDK is imported here.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .daily_brief_context import build_daily_brief_context
from .daily_brief_policy import active_consent_version, daily_brief_key


@dataclass(frozen=True)
class DailyBriefResolution:
    status: str
    narrative: str | None = None
    generated_at: str | None = None
    reason: str | None = None


def _utc_now():
    return datetime.now(timezone.utc)


class DailyBriefCoordinator:
    """Use authenticated identity, fresh domain snapshots and persistent leases.

    generation_service.generate(user_id=..., context=...) is the preferred
    boundary: it owns shared quota, provider dispatch and factual usage. The
    legacy generate/acquire_quota pair remains temporarily supported until the
    runtime is migrated. The caller supplies an authenticated User, never an ID
    received from browser input.
    """

    def __init__(self, *, store, authorization, consent_manager, load_athlete,
                 generate=None, acquire_quota=None, clock=_utc_now,
                 context_builder=build_daily_brief_context,
                 generation_service=None):
        self.store = store
        self.authorization = authorization
        self.consent_manager = consent_manager
        self.load_athlete = load_athlete
        self.generate = generate
        self.acquire_quota = acquire_quota
        self.generation_service = generation_service
        self.clock = clock
        self.context_builder = context_builder

    def _now(self):
        value = self.clock()
        if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("An aware coordinator clock is required")
        return value

    def _permitted(self, user):
        self.authorization.require_access(
            user_id=user.user_id, athlete_id=user.athlete_id,
            allowed_permissions=("owner",),
        )
        record = self.consent_manager.current(user_id=user.user_id)
        return active_consent_version(consent=record, user_id=user.user_id) is not None

    def _snapshot(self, user, zone, now):
        athlete = self.load_athlete(user)
        if athlete.athlete_id != user.athlete_id:
            raise PermissionError("Daily Brief athlete mismatch")
        context = self.context_builder(athlete, reference_day=now.astimezone(zone).date())
        key = daily_brief_key(
            athlete_id=user.athlete_id, now=now,
            timezone_name=zone.key, context_digest=context.fingerprint,
        )
        return context, key

    @staticmethod
    def _saved(payload, status):
        return DailyBriefResolution(
            status, narrative=payload["narrative"],
            generated_at=payload["generated_at"], reason=payload["reason"],
        )

    def resolve(self, *, user, timezone_name: str, enabled: bool = False):
        """Resolve once; caller may show local Today guidance for non-success."""
        if enabled is not True:
            return DailyBriefResolution("disabled")
        uses_generation_service = callable(
            getattr(self.generation_service, "generate", None)
        )
        uses_legacy_adapters = (
            callable(self.generate)
            and callable(self.acquire_quota)
        )
        if not uses_generation_service and not uses_legacy_adapters:
            return DailyBriefResolution("unavailable", reason="adapters_not_configured")
        lease = None
        try:
            now = self._now()
            zone = ZoneInfo(timezone_name)  # No silent server-time fallback.
            if not user.is_athlete or not user.athlete_id or not self._permitted(user):
                return DailyBriefResolution("blocked", reason="permission_required")
            context, key = self._snapshot(user, zone, now)
            cached = self.store.get(user_id=user.user_id, key=key)
            if cached is not None:
                return self._saved(cached, "cached")
            lease = self.store.reserve(user_id=user.user_id, key=key, now=now)
            if lease is None:
                cached = self.store.get(user_id=user.user_id, key=key)
                return (self._saved(cached, "cached") if cached is not None
                        else DailyBriefResolution("waiting", reason="reserved_or_backoff"))

            # Recheck after reservation and immediately before consuming budget.
            if not self._permitted(user):
                self.store.release(lease, now=self._now())
                return DailyBriefResolution("blocked", reason="permission_withdrawn")
            _, current_key = self._snapshot(user, zone, self._now())
            if current_key != key:
                self.store.release(lease, now=self._now())
                return DailyBriefResolution("waiting", reason="context_changed")
            if not self.store.is_active(lease, now=self._now()):
                return DailyBriefResolution("waiting", reason="lease_expired")
            if not self._permitted(user) or not self.store.is_active(lease, now=self._now()):
                self.store.release(lease, now=self._now())
                return DailyBriefResolution("blocked", reason="dispatch_cancelled")

            if uses_generation_service:
                generation = self.generation_service.generate(
                    user_id=user.user_id,
                    context=context,
                    can_dispatch=lambda: (
                        self._permitted(user)
                        and self.store.is_active(lease, now=self._now())
                        and self._snapshot(user, zone, self._now())[1] == key
                    ),
                )
                if getattr(generation, "reason", None) == "dispatch_cancelled":
                    self.store.release(lease, now=self._now())
                    return DailyBriefResolution(
                        "blocked",
                        reason="dispatch_cancelled",
                    )
                if getattr(generation, "status", None) != "generated":
                    failed_at = self._now()
                    reason = getattr(generation, "reason", None) or "generation_unavailable"
                    short_backoff = reason in {
                        "user_daily_limit",
                        "global_daily_limit",
                        "quota_unavailable",
                    }
                    self.store.fail(
                        lease,
                        now=failed_at,
                        retry_after=failed_at + timedelta(
                            minutes=5 if short_backoff else 30
                        ),
                    )
                    return DailyBriefResolution("unavailable", reason=reason)
                narrative = getattr(generation, "narrative", None)
            else:
                if self.acquire_quota(user.user_id) is not True:
                    failed_at = self._now()
                    self.store.fail(lease, now=failed_at,
                                    retry_after=failed_at + timedelta(minutes=5))
                    return DailyBriefResolution("unavailable", reason="quota_unavailable")
                narrative = self.generate(context)
            if not isinstance(narrative, str) or not narrative.strip():
                raise ValueError("Invalid Daily Brief output")
            finished_at = self._now()
            if not self._permitted(user):
                self.store.release(lease, now=finished_at)
                return DailyBriefResolution("blocked", reason="permission_withdrawn")
            _, current_key = self._snapshot(user, zone, finished_at)
            if current_key != key:
                self.store.release(lease, now=finished_at)
                return DailyBriefResolution("waiting", reason="context_changed")
            saved = self.store.complete(
                lease, narrative=narrative, reason="daily_or_context_refresh",
                now=finished_at,
            )
            if not saved:
                return DailyBriefResolution("waiting", reason="lease_expired")
            payload = self.store.get(user_id=user.user_id, key=key)
            if payload is None:
                return DailyBriefResolution("waiting", reason="result_no_longer_available")
            return self._saved(payload, "generated")
        except PermissionError:
            if lease is not None:
                try:
                    self.store.release(lease, now=self._now())
                except Exception:
                    pass  # Never bypass the failed store; token expires naturally.
            return DailyBriefResolution("blocked", reason="access_denied")
        except Exception:
            if lease is not None:
                try:
                    failed_at = self._now()
                    # Conservative retry after an uncertain provider outcome.
                    self.store.fail(lease, now=failed_at,
                                    retry_after=failed_at + timedelta(minutes=30))
                except Exception:
                    pass  # Do not expose storage errors, payloads or credentials.
            return DailyBriefResolution("unavailable", reason="resolution_failed")
