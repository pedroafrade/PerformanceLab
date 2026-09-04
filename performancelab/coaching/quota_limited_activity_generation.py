"""Reserve shared quota only at the uncached activity generation boundary.

The caller authenticates/authorises the athlete and checks the single Training
Coach consent before reaching this service. Successful quota is accounted even
if the caller later fails to persist the activity interpretation. The usage
repository participates in the caller's transaction; quota owns short separate
transactions and is never held locked across provider calls.
"""

from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)

from .activity_coach_generation import (
    ActivityCoachGenerationResult,
    ActivityCoachGenerationStatus,
)


def _now(clock):
    value = clock()
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ValueError("An aware clock is required")
    return value.astimezone(timezone.utc)


class QuotaLimitedActivityGeneration:
    def __init__(
        self,
        *,
        delegate,
        quota_store,
        usage_repository,
        limits,
        user_id,
        clock,
        timer=perf_counter,
    ):
        self.delegate = delegate
        self.quota_store = quota_store
        self.usage_repository = usage_repository
        self.limits = limits
        self.user_id = user_id
        self.clock = clock
        self.timer = timer

    @staticmethod
    def _unavailable(reason):
        return ActivityCoachGenerationResult(
            ActivityCoachGenerationStatus.UNAVAILABLE,
            error_code=reason,
        )

    def generate(self, payload):
        # A missing provider must not spend quota. The delegate supplies its
        # established provider_not_configured response without an external call.
        if self.delegate.provider is None:
            return self.delegate.generate(payload)
        try:
            started = _now(self.clock)
            admission = self.quota_store.reserve(
                user_id=self.user_id,
                request_id=str(uuid4()),
                purpose="activity",
                limits=self.limits,
                now=started,
            )
        except Exception:
            return self._unavailable("quota_unavailable")
        if not admission.permitted:
            return self._unavailable(admission.reason or "quota_unavailable")
        receipt = admission.reservation
        try:
            began = self.timer()
            result = self.delegate.generate(payload)
            ended = _now(self.clock)
            elapsed = max(0, round((self.timer() - began) * 1000))
            generated = (
                result.status is ActivityCoachGenerationStatus.GENERATED
                and result.narrative is not None
            )
            # Only these provider rejections establish no successful generation.
            # Timeout, malformed response and generic failures remain uncertain.
            confirmed_no_generation = (
                not generated
                and result.error_code
                in {
                    "provider_configuration",
                    "provider_authentication",
                    "provider_quota",
                    "provider_request",
                    "provider_not_configured",
                }
            )
            provider = self.delegate.provider
            metadata = result.narrative if generated else provider
            provider_name = (
                metadata.provider
                if generated
                else getattr(metadata, "provider_name", None)
            )
            model_name = (
                metadata.model
                if generated
                else getattr(metadata, "model_name", None)
            )
            event = TrainingCoachUsageEvent(
                user_id=self.user_id,
                usage_id=receipt.request_id,
                occurred_at=started,
                purpose="activity",
                status=(
                    TrainingCoachUsageStatus.GENERATED
                    if generated
                    else TrainingCoachUsageStatus.FAILED
                ),
                provider=provider_name,
                model=model_name,
                error_code=(
                    None
                    if generated
                    else result.error_code or "generation_failed"
                ),
                latency_ms=elapsed,
                remaining_user_requests=admission.remaining_user_requests,
                remaining_global_requests=admission.remaining_global_requests,
            )
            self.usage_repository.save(event)
            if generated:
                if not self.quota_store.finish(
                    receipt,
                    outcome="generated",
                    now=ended,
                ):
                    return self._unavailable("quota_finalization_failed")
            elif confirmed_no_generation:
                # If expired, finish returns False and conservatively keeps the
                # budget charged. Do not claim the slot has been returned.
                self.quota_store.finish(
                    receipt,
                    outcome="not_generated",
                    now=ended,
                )
            if (
                result.status is ActivityCoachGenerationStatus.GENERATED
                and not generated
            ):
                return self._unavailable("generation_failed")
            return result
        except Exception:
            # Never retry here or release an ambiguous request. Do not expose
            # database/provider exceptions and do not publish unrecorded text.
            return self._unavailable("generation_accounting_failed")
