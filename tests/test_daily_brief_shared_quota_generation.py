from datetime import datetime, timezone
from types import SimpleNamespace

from performancelab.coaching.quota_limited_daily_brief_generation import (
    QuotaLimitedDailyBriefGeneration,
)
from performancelab.storage.training_coach_quota_store import QuotaAdmission
from performancelab.training_coach_usage import TrainingCoachUsageStatus
from performancelab.training_coach_usage_limits import TrainingCoachUsageLimits


NOW = datetime(2026, 9, 4, 9, tzinfo=timezone.utc)


class Quota:
    def __init__(self, *, permitted=True, reason=None, finalised=True):
        self.permitted = permitted
        self.reason = reason
        self.finalised = finalised
        self.reserved = []
        self.finished = []

    def reserve(self, **values):
        self.reserved.append(values)
        receipt = SimpleNamespace(request_id=values["request_id"])
        return QuotaAdmission(
            self.permitted,
            self.reason,
            receipt if self.permitted else None,
            2,
            7,
        )

    def finish(self, receipt, *, outcome, now):
        self.finished.append((receipt, outcome, now))
        return self.finalised


class Usage:
    def __init__(self, *, fail=False):
        self.fail = fail
        self.events = []

    def save(self, event):
        if self.fail:
            raise RuntimeError("storage unavailable")
        self.events.append(event)


class Provider:
    provider_name = "google-gemini"
    model_name = "fake-model"

    def __init__(self, recorder, *, outcome="generated"):
        self.recorder = recorder
        self.outcome = outcome
        self.calls = 0

    def __call__(self, context):
        self.calls += 1
        status = self.outcome
        self.recorder({
            "purpose": "daily_brief",
            "provider": self.provider_name,
            "model": self.model_name,
            "status": status,
            "prompt_tokens": 20,
            "output_tokens": 10,
            "total_tokens": 30,
        })
        if status != "generated":
            raise RuntimeError(status)
        return "Today's concise guidance."


def service(*, quota, usage, outcome="generated", providers=None):
    def factory(*, record_usage):
        provider = Provider(record_usage, outcome=outcome)
        if providers is not None:
            providers.append(provider)
        return provider

    return QuotaLimitedDailyBriefGeneration(
        quota_store=quota,
        usage_repository=usage,
        usage_limits=TrainingCoachUsageLimits(
            user_daily_limit=3,
            global_daily_limit=8,
        ),
        provider_factory=factory,
        clock=lambda: NOW,
        timer=iter((1.0, 1.2)).__next__,
    )


def test_generated_brief_uses_one_shared_reservation_and_usage_id():
    quota = Quota()
    usage = Usage()
    providers = []

    result = service(
        quota=quota,
        usage=usage,
        providers=providers,
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)

    assert result.status == "generated"
    assert result.narrative == "Today's concise guidance."
    assert providers[0].calls == 1
    assert quota.reserved[0]["purpose"] == "daily_brief"
    assert quota.finished[0][1] == "generated"
    assert usage.events[0].usage_id == quota.reserved[0]["request_id"]
    assert usage.events[0].status is TrainingCoachUsageStatus.GENERATED
    assert usage.events[0].purpose == "daily_brief"
    assert usage.events[0].prompt_tokens == 20
    assert usage.events[0].total_tokens == 30


def test_rejected_quota_never_constructs_or_calls_provider():
    quota = Quota(permitted=False, reason="global_daily_limit")
    providers = []

    result = service(
        quota=quota,
        usage=Usage(),
        providers=providers,
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)

    assert result.status == "unavailable"
    assert result.reason == "global_daily_limit"
    assert providers == []


def test_confirmed_provider_rejection_releases_capacity():
    quota = Quota()
    usage = Usage()

    result = service(
        quota=quota,
        usage=usage,
        outcome="provider_authentication",
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)

    assert result.reason == "provider_authentication"
    assert quota.finished[0][1] == "not_generated"
    assert usage.events[0].status is TrainingCoachUsageStatus.FAILED


def test_ambiguous_failure_remains_charged_and_is_not_retried():
    quota = Quota()
    usage = Usage()
    providers = []

    result = service(
        quota=quota,
        usage=usage,
        outcome="provider_response",
        providers=providers,
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)

    assert result.reason == "generation_failed"
    assert providers[0].calls == 1
    assert quota.finished == []


def test_unrecorded_or_unfinalised_text_is_never_published():
    failed_usage = service(
        quota=Quota(),
        usage=Usage(fail=True),
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)
    failed_finalisation = service(
        quota=Quota(finalised=False),
        usage=Usage(),
    ).generate(user_id="user-1", context=object(), can_dispatch=lambda: True)

    assert failed_usage.narrative is None
    assert failed_usage.reason == "usage_recording_failed"
    assert failed_finalisation.narrative is None
    assert failed_finalisation.reason == "quota_finalization_failed"


def test_dispatch_is_rechecked_after_reservation_and_before_provider():
    quota = Quota()
    usage = Usage()
    providers = []

    result = service(
        quota=quota,
        usage=usage,
        providers=providers,
    ).generate(
        user_id="user-1",
        context=object(),
        can_dispatch=lambda: False,
    )

    assert result.reason == "dispatch_cancelled"
    assert providers == []
    assert usage.events[0].error_code == "dispatch_cancelled"
    assert quota.finished[0][1] == "not_generated"
