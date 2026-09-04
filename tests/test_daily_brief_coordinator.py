"""Coordinator integration with real SQL leases and a fake generation adapter."""

import ast
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from runpy import run_path
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[1]
# Reuse the SQL test harness by explicit path, not pytest-dependent module names.
SQL = run_path(str(Path(__file__).with_name("test_daily_brief_store.py")))
load = SQL["load"]
model = load("performancelab/training_coach_consent.py")
Consent = model["TrainingCoachConsent"]
policy = load("performancelab/coaching/daily_brief_policy.py",
              TrainingCoachConsent=Consent,
              TRAINING_COACH_CONSENT_VERSION=model["TRAINING_COACH_CONSENT_VERSION"])
tree = ast.parse((ROOT / "performancelab/coaching/daily_brief_coordinator.py").read_text(encoding="utf-8"))
tree.body = [n for n in tree.body if not (isinstance(n, ast.ImportFrom) and n.level)]
namespace = dict(__name__=__name__, build_daily_brief_context=None,
                 active_consent_version=policy["active_consent_version"],
                 daily_brief_key=policy["daily_brief_key"])
exec(compile(tree, "coordinator", "exec"), namespace)
Coordinator = namespace["DailyBriefCoordinator"]
NOW = datetime(2026, 9, 4, 10, tzinfo=timezone.utc)


@pytest.fixture
def harness(tmp_path):
    fixture = SQL["engine"].__wrapped__(tmp_path)
    engine = next(fixture)
    clock = SimpleNamespace(value=NOW)
    user = SimpleNamespace(user_id="user-a", athlete_id="athlete-a", is_athlete=True)
    athlete = SimpleNamespace(athlete_id="athlete-a", revision="one")
    consent = SimpleNamespace(record=Consent(user_id="user-a", granted_at=NOW))
    store = SQL["Store"](engine)
    authorization = MagicMock()
    quota = MagicMock(return_value=True)
    generate = MagicMock(return_value="Daily guidance")
    loader = MagicMock(return_value=athlete)
    manager = SimpleNamespace(current=lambda **_: consent.record)
    def context_builder(athlete, *, reference_day):
        return SimpleNamespace(reference_day=reference_day,
                               fingerprint=sha256(athlete.revision.encode()).hexdigest())
    coordinator = Coordinator(
        store=store, authorization=authorization, consent_manager=manager,
        load_athlete=loader, generate=generate, acquire_quota=quota,
        clock=lambda: clock.value, context_builder=context_builder,
    )
    h = SimpleNamespace(coordinator=coordinator, user=user, athlete=athlete,
                        clock=clock, consent=consent, store=store, quota=quota,
                        generate=generate, loader=loader, authorization=authorization)
    yield h
    try:
        next(fixture)
    except StopIteration:
        pass


def resolve(h, **kwargs):
    return h.coordinator.resolve(user=h.user, timezone_name=kwargs.pop("timezone_name", "UTC"),
                                 enabled=kwargs.pop("enabled", True), **kwargs)


def test_disabled_default_has_no_side_effects(harness):
    h = harness
    assert h.coordinator.resolve(user=h.user, timezone_name="UTC").status == "disabled"
    h.loader.assert_not_called()
    h.generate.assert_not_called()
    h.quota.assert_not_called()


@pytest.mark.parametrize("enabled", ["false", "true", 1, None])
def test_feature_requires_explicit_boolean_true(harness, enabled):
    assert resolve(harness, enabled=enabled).status == "disabled"
    harness.generate.assert_not_called()


def test_missing_quota_adapter_fails_closed(harness):
    h = harness
    h.coordinator.acquire_quota = None
    assert resolve(h).reason == "adapters_not_configured"
    h.generate.assert_not_called()


def test_missing_or_legacy_consent_blocks(harness):
    h = harness
    h.consent.record = None
    assert resolve(h).status == "blocked"
    h.consent.record = Consent(user_id="user-a", granted_at=NOW,
                               policy_version="training-coach-consent-v1")
    assert resolve(h).status == "blocked"
    h.generate.assert_not_called()


def test_generate_then_reuse_without_new_quota_or_request(harness):
    h = harness
    assert resolve(h).status == "generated"
    h.clock.value += timedelta(hours=1)
    result = resolve(h)
    assert result.status == "cached" and result.narrative == "Daily guidance"
    assert result.generated_at == NOW.isoformat()
    h.generate.assert_called_once()
    h.quota.assert_called_once_with("user-a")


def test_shared_generation_service_replaces_legacy_quota_pair(harness):
    h = harness
    service = MagicMock()
    dispatch_checks = []
    def generate_with_dispatch_check(**arguments):
        dispatch_checks.append(arguments["can_dispatch"]())
        return SimpleNamespace(
            status="generated",
            narrative="Shared quota guidance",
            reason=None,
        )
    service.generate.side_effect = generate_with_dispatch_check
    h.coordinator.generation_service = service
    h.coordinator.generate = None
    h.coordinator.acquire_quota = None

    first = resolve(h)
    second = resolve(h)

    assert first.status == "generated"
    assert first.narrative == "Shared quota guidance"
    assert second.status == "cached"
    service.generate.assert_called_once()
    assert service.generate.call_args.kwargs["user_id"] == "user-a"
    assert dispatch_checks == [True]
    h.quota.assert_not_called()


@pytest.mark.parametrize(
    ("reason", "retry_minutes"),
    (
        ("global_daily_limit", 5),
        ("generation_failed", 30),
    ),
)
def test_shared_generation_failure_uses_bounded_backoff(
    harness,
    reason,
    retry_minutes,
):
    h = harness
    service = MagicMock()
    service.generate.return_value = SimpleNamespace(
        status="unavailable",
        narrative=None,
        reason=reason,
    )
    h.coordinator.generation_service = service

    result = resolve(h)

    assert result.status == "unavailable"
    assert result.reason == reason
    h.clock.value += timedelta(minutes=retry_minutes - 1)
    assert resolve(h).status == "waiting"
    h.clock.value += timedelta(minutes=1)
    assert resolve(h).status == "unavailable"
    assert service.generate.call_count == 2


def test_shared_service_rechecks_permission_immediately_before_dispatch(harness):
    h = harness
    service = MagicMock()
    def cancel_before_dispatch(**arguments):
        h.consent.record = h.consent.record.withdraw(withdrawn_at=NOW)
        assert arguments["can_dispatch"]() is False
        return SimpleNamespace(
            status="unavailable",
            narrative=None,
            reason="dispatch_cancelled",
        )
    service.generate.side_effect = cancel_before_dispatch
    h.coordinator.generation_service = service

    result = resolve(h)

    assert result.status == "blocked"
    assert result.reason == "dispatch_cancelled"
    assert h.store.export_for_user("user-a") == []


def test_next_local_day_and_changed_foundations_regenerate(harness):
    h = harness
    resolve(h)
    h.athlete.revision = "changed"
    assert resolve(h).status == "generated"
    h.clock.value += timedelta(days=1)
    assert resolve(h).status == "generated"
    assert h.generate.call_count == 3


def test_local_day_does_not_use_server_date(harness):
    h = harness
    h.clock.value = datetime(2026, 9, 5, 0, 30, tzinfo=timezone.utc)
    assert resolve(h, timezone_name="America/New_York").status == "generated"
    assert h.store.export_for_user("user-a")[0]["key"]["local_day"] == "2026-09-04"


def test_quota_denial_never_calls_provider(harness):
    h = harness
    h.quota.return_value = False
    assert resolve(h).reason == "quota_unavailable"
    assert resolve(h).status == "waiting"
    h.generate.assert_not_called()


def test_context_changed_during_generation_is_not_saved(harness):
    h = harness
    def generate(_):
        h.athlete.revision = "new plan"
        return "Old context guidance"
    h.generate.side_effect = generate
    result = resolve(h)
    assert result.reason == "context_changed"
    assert h.store.export_for_user("user-a") == []


def test_withdrawal_during_generation_discards_result(harness):
    h = harness
    def generate(_):
        h.consent.record = h.consent.record.withdraw(withdrawn_at=NOW)
        return "Should not be saved"
    h.generate.side_effect = generate
    assert resolve(h).reason == "permission_withdrawn"
    assert h.store.export_for_user("user-a") == []


def test_provider_exception_is_private_and_retry_is_delayed(harness):
    h = harness
    h.generate.side_effect = RuntimeError("SECRET credential in provider error")
    result = resolve(h)
    assert result.status == "unavailable"
    assert "SECRET" not in repr(result)
    assert resolve(h).status == "waiting"
    h.generate.assert_called_once()


def test_expired_lease_cannot_publish(harness):
    h = harness
    def generate(_):
        h.clock.value += timedelta(minutes=6)
        return "Too late"
    h.generate.side_effect = generate
    assert resolve(h).reason == "lease_expired"
    assert h.store.export_for_user("user-a") == []


def test_different_athlete_and_denied_access_fail_closed(harness):
    h = harness
    h.athlete.athlete_id = "athlete-b"
    assert resolve(h).reason == "access_denied"
    h.generate.assert_not_called()
    h.authorization.require_access.side_effect = PermissionError("No access")
    assert resolve(h).reason == "access_denied"


def test_two_sessions_only_dispatch_once(harness):
    h = harness
    started, finish = Event(), Event()
    def generate(_):
        started.set()
        assert finish.wait(5)
        return "Single request"
    h.generate.side_effect = generate
    with ThreadPoolExecutor(max_workers=1) as pool:
        first = pool.submit(resolve, h)
        try:
            assert started.wait(5)
            assert resolve(h).status == "waiting"
        finally:
            finish.set()
        assert first.result(timeout=5).status == "generated"
    h.generate.assert_called_once()
    h.quota.assert_called_once()


def test_release_and_active_checks_are_token_scoped(harness):
    h = harness
    key = SQL["key"]()
    first = h.store.reserve(user_id="user-a", key=key, now=NOW,
                            lease_duration=timedelta(seconds=1))
    later = NOW + timedelta(seconds=2)
    second = h.store.reserve(user_id="user-a", key=key, now=later)
    assert not h.store.is_active(first, now=later)
    assert not h.store.release(first, now=later)
    assert h.store.is_active(second, now=later)
    assert h.store.release(second, now=later)
    assert not h.store.is_active(second, now=later)
