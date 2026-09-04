"""Quota and factual accounting boundary for one Daily Brief generation.

This service is intentionally not connected to login or Dashboard yet.  The
caller supplies the authenticated user ID; the provider receives only the
already-minimised internal context.  Quota transactions remain short and no
database lock is held during the external request.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)


@dataclass(frozen=True)
class DailyBriefGenerationResult:
    status: str
    narrative: str | None = None
    reason: str | None = None


def _now(clock):
    value = clock()
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError("An aware Daily Brief clock is required")
    return value.astimezone(timezone.utc)


class QuotaLimitedDailyBriefGeneration:
    """Admit, generate, record and finalise one Daily Brief request."""

    _CONFIRMED_NO_GENERATION = {
        "provider_configuration",
        "provider_authentication",
        "provider_quota",
        "provider_request",
    }

    def __init__(
        self,
        *,
        quota_store,
        usage_repository,
        usage_limits,
        provider_factory,
        clock,
        timer=perf_counter,
    ):
        if not callable(provider_factory):
            raise TypeError("provider_factory must be callable")
        if not callable(clock) or not callable(timer):
            raise TypeError("Daily Brief clocks must be callable")
        self.quota_store = quota_store
        self.usage_repository = usage_repository
        self.usage_limits = usage_limits
        self.provider_factory = provider_factory
        self.clock = clock
        self.timer = timer

    @staticmethod
    def _unavailable(reason):
        return DailyBriefGenerationResult("unavailable", reason=reason)

    def generate(self, *, user_id, context, can_dispatch):
        if not callable(can_dispatch):
            return self._unavailable("dispatch_guard_required")
        try:
            started_at = _now(self.clock)
            admission = self.quota_store.reserve(
                user_id=user_id,
                request_id=str(uuid4()),
                purpose="daily_brief",
                limits=self.usage_limits,
                now=started_at,
            )
        except Exception:
            return self._unavailable("quota_unavailable")

        if not admission.permitted:
            return self._unavailable(admission.reason or "quota_unavailable")

        receipt = admission.reservation
        recorded_event = None
        recording_attempted = False
        provider = None
        began = self.timer()

        def record_usage(metadata):
            nonlocal recorded_event, recording_attempted
            if recorded_event is not None:
                raise ValueError("Daily Brief usage was already recorded")
            if not isinstance(metadata, dict) or metadata.get("purpose") != "daily_brief":
                raise ValueError("Invalid Daily Brief usage metadata")
            generated = metadata.get("status") == "generated"
            recording_attempted = True
            event = TrainingCoachUsageEvent(
                user_id=user_id,
                usage_id=receipt.request_id,
                occurred_at=started_at,
                purpose="daily_brief",
                status=(
                    TrainingCoachUsageStatus.GENERATED
                    if generated
                    else TrainingCoachUsageStatus.FAILED
                ),
                provider=metadata.get("provider"),
                model=metadata.get("model"),
                error_code=None if generated else metadata.get("status"),
                latency_ms=max(0, round((self.timer() - began) * 1000)),
                remaining_user_requests=admission.remaining_user_requests,
                remaining_global_requests=admission.remaining_global_requests,
                prompt_tokens=metadata.get("prompt_tokens"),
                output_tokens=metadata.get("output_tokens"),
                total_tokens=metadata.get("total_tokens"),
            )
            self.usage_repository.save(event)
            recorded_event = event

        try:
            try:
                dispatch_permitted = can_dispatch() is True
            except Exception:
                dispatch_permitted = False
            if not dispatch_permitted:
                record_usage({
                    "purpose": "daily_brief",
                    "provider": None,
                    "model": None,
                    "status": "dispatch_cancelled",
                    "prompt_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                })
                self.quota_store.finish(
                    receipt,
                    outcome="not_generated",
                    now=_now(self.clock),
                )
                return self._unavailable("dispatch_cancelled")
            provider = self.provider_factory(record_usage=record_usage)
            narrative = provider(context)
            finished_at = _now(self.clock)
            if (
                not isinstance(narrative, str)
                or not narrative.strip()
                or recorded_event is None
                or recorded_event.status is not TrainingCoachUsageStatus.GENERATED
            ):
                return self._unavailable("usage_recording_missing")
            if not self.quota_store.finish(
                receipt,
                outcome="generated",
                now=finished_at,
            ):
                return self._unavailable("quota_finalization_failed")
            return DailyBriefGenerationResult(
                "generated",
                narrative=narrative.strip(),
            )
        except Exception as error:
            reason = getattr(error, "args", (None,))[0]
            if reason not in self._CONFIRMED_NO_GENERATION:
                reason = (
                    "usage_recording_failed"
                    if str(error) == "usage_recording_failed"
                    else "generation_failed"
                )
            if recorded_event is None and not recording_attempted:
                try:
                    record_usage({
                        "purpose": "daily_brief",
                        "provider": getattr(provider, "provider_name", None),
                        "model": getattr(provider, "model_name", None),
                        "status": reason,
                        "prompt_tokens": None,
                        "output_tokens": None,
                        "total_tokens": None,
                    })
                except Exception:
                    return self._unavailable("usage_recording_failed")
            elif recorded_event is None:
                return self._unavailable("usage_recording_failed")
            if reason in self._CONFIRMED_NO_GENERATION:
                try:
                    self.quota_store.finish(
                        receipt,
                        outcome="not_generated",
                        now=_now(self.clock),
                    )
                except Exception:
                    pass
            return self._unavailable(reason)
