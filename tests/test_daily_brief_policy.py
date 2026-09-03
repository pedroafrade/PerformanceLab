"""Scheduling contracts only: these tests never contact a provider."""

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

import pytest


# Load the dependency-free module without importing optional provider packages.
_path = Path(__file__).resolve().parents[1] / "performancelab/coaching/daily_brief_policy.py"
_spec = spec_from_file_location("_daily_brief_policy_tests", _path)
policy = module_from_spec(_spec)
sys.modules[_spec.name] = policy
_spec.loader.exec_module(policy)

NOW = datetime(2026, 9, 4, 0, 30, tzinfo=timezone.utc)


def key(**kwargs):
    return policy.daily_brief_key(
        athlete_id="athlete-a", now=NOW, timezone_name="UTC",
        context_digest=kwargs.get("digest", "context-a"),
    )


def decision(**kwargs):
    return policy.decide_daily_brief(
        requested=kwargs.pop("requested", key()), now=NOW,
        enabled=kwargs.pop("enabled", True),
        consent_version=kwargs.pop("consent_version", policy.CONSENT_VERSION),
        **kwargs,
    )


def fingerprint(**kwargs):
    values = dict(plan={"phase": "peak"}, profile={"goal": "race"},
                  activities=[{"id": "a", "load": 100}], reports=[])
    values.update(kwargs)
    return policy.context_fingerprint(**values)


@pytest.mark.parametrize("consent", [None, "training-coach-consent-v1", "old-version"])
def test_manual_or_outdated_consent_does_not_authorize_automatic_requests(consent):
    result = decision(consent_version=consent, saved=key())
    assert result.action == policy.BriefAction.BLOCK
    assert result.reason == "automatic_consent_required"


def test_feature_is_off_by_default():
    result = policy.decide_daily_brief(requested=key(), now=NOW)
    assert result.reason == "feature_disabled"


def test_first_brief_is_eligible_but_not_executed():
    assert decision().reason == "first_brief"
    assert decision().action == policy.BriefAction.GENERATE


def test_same_day_same_context_reuses_across_hours():
    later = policy.daily_brief_key(athlete_id="athlete-a", now=NOW + timedelta(hours=8),
                                  timezone_name="UTC", context_digest="context-a")
    assert decision(requested=later, saved=key()).action == policy.BriefAction.REUSE


def test_new_day_requires_a_new_brief():
    assert decision(saved=replace(key(), local_day=key().local_day - timedelta(days=1))).reason == "new_local_day"


def test_relevant_change_requires_a_new_brief():
    assert decision(saved=key(digest="old")).reason == "relevant_context_changed"


def test_context_contract_upgrade_invalidates_saved_brief():
    assert decision(saved=replace(key(), context_version="old")).reason == "context_version_changed"


def test_different_athlete_fails_closed():
    assert decision(saved=replace(key(), athlete_id="other")).reason == "athlete_mismatch"


def test_local_day_uses_configured_timezone():
    local = policy.daily_brief_key(athlete_id="a", now=NOW,
                                  timezone_name="America/New_York", context_digest="x")
    assert local.local_day.isoformat() == "2026-09-03"


def test_unknown_timezone_does_not_fall_back_to_server():
    with pytest.raises(KeyError):
        policy.daily_brief_key(athlete_id="a", now=NOW, timezone_name="Invalid/Zone",
                              context_digest="x")


def test_naive_time_rejected():
    with pytest.raises(ValueError):
        policy.daily_brief_key(athlete_id="a", now=NOW.replace(tzinfo=None),
                              timezone_name="UTC", context_digest="x")


def test_backoff_applies_even_after_context_changes():
    assert decision(saved=key(digest="old"), retry_not_before=NOW + timedelta(minutes=5)).action == policy.BriefAction.WAIT
    assert decision(saved=key(digest="old"), retry_not_before=NOW).action == policy.BriefAction.GENERATE


def test_valid_saved_brief_can_be_reused_during_backoff():
    assert decision(saved=key(), retry_not_before=NOW + timedelta(minutes=5)).action == policy.BriefAction.REUSE


def test_reordering_import_or_mapping_does_not_change_fingerprint():
    a = {"id": "a", "load": 100}
    b = {"load": 200, "id": "b"}
    assert fingerprint(activities=[a, b]) == fingerprint(activities=[b, a])
    assert fingerprint(plan={"a": 1, "b": 2}) == fingerprint(plan={"b": 2, "a": 1})


@pytest.mark.parametrize("change", [
    {"plan": {"phase": "taper"}},
    {"profile": {"goal": "new race"}},
    {"activities": []},
    {"activities": [{"id": "a", "load": 101}]},
    {"reports": [{"date": "2026-09-03", "text": "reported discomfort"}]},
])
def test_foundational_changes_change_fingerprint(change):
    assert fingerprint(**change) != fingerprint()


def test_invalid_numeric_context_rejected():
    with pytest.raises(ValueError):
        fingerprint(plan={"load": float("nan")})
