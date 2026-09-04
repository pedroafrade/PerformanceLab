from datetime import datetime, timezone
from types import SimpleNamespace

from performancelab import Athlete
from performancelab.application import GenerateActivityCoachInterpretation
from performancelab.coaching import (
    ActivityCoachCoordinator,
    ActivityCoachGenerationResult,
    ActivityCoachGenerationService,
    ActivityCoachGenerationStatus,
    ActivityCoachNarrative,
    ActivityCoachResolutionStatus,
)
from performancelab.coaching.quota_limited_activity_generation import (
    QuotaLimitedActivityGeneration,
)
from performancelab.storage.training_coach_quota_store import (
    QuotaAdmission,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageStatus,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageLimits,
)


NOW = datetime(2026, 9, 4, 8, tzinfo=timezone.utc)


class Delegate:
    def __init__(self, result, *, configured=True):
        self.provider = (
            SimpleNamespace(provider_name="fake", model_name="model")
            if configured
            else None
        )
        self.result = result
        self.calls = 0

    def generate(self, payload):
        self.calls += 1
        return self.result


class QuotaStore:
    def __init__(self, *, permitted=True, reason=None, finish_result=True):
        self.permitted = permitted
        self.reason = reason
        self.finish_result = finish_result
        self.reservations = []
        self.finished = []

    def reserve(self, **values):
        self.reservations.append(values)
        receipt = SimpleNamespace(request_id=values["request_id"])
        return QuotaAdmission(
            permitted=self.permitted,
            reason=self.reason,
            reservation=receipt if self.permitted else None,
            remaining_user_requests=2,
            remaining_global_requests=7,
        )

    def finish(self, receipt, *, outcome, now):
        self.finished.append((receipt, outcome, now))
        return self.finish_result


class UsageRepository:
    def __init__(self, *, fail=False):
        self.fail = fail
        self.events = []

    def save(self, event):
        if self.fail:
            raise RuntimeError("database unavailable")
        self.events.append(event)


def narrative_result():
    return ActivityCoachGenerationResult(
        status=ActivityCoachGenerationStatus.GENERATED,
        narrative=ActivityCoachNarrative(
            measured_facts="Facts.",
            deterministic_signals="Signals.",
            prudent_interpretation="Interpretation.",
            recommendations="Recommendation.",
            data_limitations="Limitations.",
            provider="fake",
            model="model",
        ),
    )


def generation(*, delegate, quota, usage):
    return QuotaLimitedActivityGeneration(
        delegate=delegate,
        quota_store=quota,
        usage_repository=usage,
        limits=TrainingCoachUsageLimits(
            user_daily_limit=3,
            global_daily_limit=8,
        ),
        user_id="user-1",
        clock=lambda: NOW,
        timer=iter((1.0, 1.25)).__next__,
    )


def test_success_reserves_once_and_uses_request_id_for_usage():
    delegate = Delegate(narrative_result())
    quota = QuotaStore()
    usage = UsageRepository()

    result = generation(delegate=delegate, quota=quota, usage=usage).generate({})

    assert result.status is ActivityCoachGenerationStatus.GENERATED
    assert delegate.calls == 1
    assert quota.reservations[0]["purpose"] == "activity"
    assert quota.finished[0][1] == "generated"
    assert len(usage.events) == 1
    event = usage.events[0]
    assert event.usage_id == quota.reservations[0]["request_id"]
    assert event.status is TrainingCoachUsageStatus.GENERATED
    assert event.purpose == "activity"
    assert event.latency_ms == 250
    assert event.remaining_user_requests == 2
    assert event.remaining_global_requests == 7


def test_limit_blocks_provider_without_recording_a_result():
    delegate = Delegate(narrative_result())
    quota = QuotaStore(permitted=False, reason="user_daily_limit")
    usage = UsageRepository()

    result = generation(delegate=delegate, quota=quota, usage=usage).generate({})

    assert result.status is ActivityCoachGenerationStatus.UNAVAILABLE
    assert result.error_code == "user_daily_limit"
    assert delegate.calls == 0
    assert usage.events == []


def test_known_rejection_releases_reservation_but_uncertain_failure_does_not():
    for error_code, expected_finishes in (
        ("provider_authentication", 1),
        ("provider_unavailable", 0),
    ):
        delegate = Delegate(ActivityCoachGenerationResult(
            status=ActivityCoachGenerationStatus.UNAVAILABLE,
            error_code=error_code,
        ))
        quota = QuotaStore()
        usage = UsageRepository()

        result = generation(delegate=delegate, quota=quota, usage=usage).generate({})

        assert result.error_code == error_code
        assert len(quota.finished) == expected_finishes
        if quota.finished:
            assert quota.finished[0][1] == "not_generated"
        assert usage.events[0].status is TrainingCoachUsageStatus.FAILED


def test_unconfigured_provider_never_reserves_quota():
    result = ActivityCoachGenerationResult(
        status=ActivityCoachGenerationStatus.UNAVAILABLE,
        error_code="provider_not_configured",
    )
    delegate = Delegate(result, configured=False)
    quota = QuotaStore()

    actual = generation(
        delegate=delegate,
        quota=quota,
        usage=UsageRepository(),
    ).generate({})

    assert actual is result
    assert delegate.calls == 1
    assert quota.reservations == []


def test_unrecorded_generation_is_not_published_or_retried():
    delegate = Delegate(narrative_result())
    quota = QuotaStore()

    result = generation(
        delegate=delegate,
        quota=quota,
        usage=UsageRepository(fail=True),
    ).generate({})

    assert result.status is ActivityCoachGenerationStatus.UNAVAILABLE
    assert result.error_code == "generation_accounting_failed"
    assert delegate.calls == 1
    assert quota.finished == []


def test_failed_quota_finalisation_does_not_publish_generated_text():
    delegate = Delegate(narrative_result())
    quota = QuotaStore(finish_result=False)

    result = generation(
        delegate=delegate,
        quota=quota,
        usage=UsageRepository(),
    ).generate({})

    assert result.status is ActivityCoachGenerationStatus.UNAVAILABLE
    assert result.error_code == "quota_finalization_failed"
    assert delegate.calls == 1


class Provider:
    provider_name = "fake"
    model_name = "model"

    def __init__(self):
        self.calls = 0

    def generate(self, payload):
        self.calls += 1
        return narrative_result().narrative


def test_use_case_checks_cache_before_reserving_shared_quota():
    provider = Provider()
    quota = QuotaStore()
    usage = UsageRepository()
    use_case = GenerateActivityCoachInterpretation(
        coordinator=ActivityCoachCoordinator(
            generation_service=ActivityCoachGenerationService(provider),
            now=lambda: NOW,
        ),
        usage_repository=usage,
        usage_limits=TrainingCoachUsageLimits(
            user_daily_limit=3,
            global_daily_limit=8,
        ),
        quota_store=quota,
        clock=lambda: NOW,
        timer=iter((1.0, 1.25)).__next__,
    )
    athlete = Athlete(name="Pedro")
    arguments = {
        "user_id": "user-1",
        "athlete": athlete,
        "workout_id": "workout-1",
        "payload": {"contract_version": "activity-coach-v1"},
    }

    first = use_case.execute(**arguments)
    second = use_case.execute(**arguments)

    assert first.status is ActivityCoachResolutionStatus.GENERATED
    assert second.status is ActivityCoachResolutionStatus.STORED
    assert provider.calls == 1
    assert len(quota.reservations) == 1
    assert len(usage.events) == 1
