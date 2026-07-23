"""
Tests for RegenerationStrategy.

Place this file at:
    tests/coaching/strategies/test_regeneration_strategy.py
"""

from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.regeneration import (
    RegenerationStrategy,
)
from performancelab.coaching.strategy import StrategyPlan


def make_context(
    *,
    tsb: float = 0.0,
    average_rpe: float | None = None,
    days_until_event: int | None = None,
):
    """
    Creates the minimum context required by RegenerationStrategy.
    """

    return SimpleNamespace(
        tsb=tsb,
        average_rpe=average_rpe,
        days_until_event=days_until_event,
    )


# ======================================================
# Default regeneration week
# ======================================================


def test_build_returns_strategy_plan():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert isinstance(
        plan,
        StrategyPlan,
    )


def test_build_uses_strategy_identity():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.strategy == "RegenerationStrategy"
    assert plan.phase == "Regeneration"


def test_default_regeneration_targets():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.volume_factor == pytest.approx(0.60)
    assert plan.target_sessions == 4
    assert plan.intensity_sessions == 0
    assert plan.long_sessions == 0
    assert plan.recovery_days == 3


def test_default_regeneration_metadata():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.focus == "recovery"
    assert plan.target_weekly_minutes == 240
    assert plan.target_weekly_load == pytest.approx(150.0)
    assert plan.long_session_minutes is None


def test_default_regeneration_objectives():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.objectives == (
        "Reduce accumulated fatigue.",
        "Restore readiness for future training.",
        "Maintain movement without creating new stress.",
    )


def test_default_regeneration_guidelines():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert len(plan.guidelines) == 4

    assert any(
        "rest or short easy sessions" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "Avoid threshold, interval and maximal strength" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "Resume normal training only when recovery" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "low-impact training" in guideline
        for guideline in plan.guidelines
    )


def test_default_regeneration_warning():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.warnings == (
        (
            "Regeneration takes priority over planned "
            "training progression."
        ),
    )


# ======================================================
# Very high accumulated fatigue
# ======================================================


def test_very_low_tsb_reduces_volume():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-30.1,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.40)


def test_very_low_tsb_reduces_sessions():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-30.1,
        ),
    )

    assert plan.target_sessions == 3
    assert plan.recovery_days == 4


def test_very_low_tsb_reduces_weekly_targets():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-30.1,
        ),
    )

    assert plan.target_weekly_minutes == 180
    assert plan.target_weekly_load == pytest.approx(100.0)


def test_very_low_tsb_adds_warning():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-30.1,
        ),
    )

    assert "Accumulated fatigue is very high." in plan.warnings


def test_tsb_boundary_does_not_trigger_extreme_reduction():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-30.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.60)
    assert plan.target_sessions == 4
    assert plan.recovery_days == 3
    assert plan.target_weekly_minutes == 240


# ======================================================
# High perceived effort
# ======================================================


def test_high_rpe_reduces_volume():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.50)


def test_high_rpe_keeps_default_session_counts():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.target_sessions == 4
    assert plan.recovery_days == 3


def test_high_rpe_updates_weekly_load():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.target_weekly_minutes == 240
    assert plan.target_weekly_load == pytest.approx(125.0)


def test_high_rpe_adds_warning():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert (
        "Recent sessions have a high perceived effort."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_volume():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=7.9,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.60)
    assert (
        "Recent sessions have a high perceived effort."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=None,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.60)


# ======================================================
# Upcoming event
# ======================================================


def test_near_event_adds_warning():
    plan = RegenerationStrategy().build(
        make_context(
            days_until_event=7,
        ),
    )

    assert (
        "An event is approaching while fatigue remains elevated."
        in plan.warnings
    )


def test_event_inside_seven_days_adds_warning():
    plan = RegenerationStrategy().build(
        make_context(
            days_until_event=3,
        ),
    )

    assert (
        "An event is approaching while fatigue remains elevated."
        in plan.warnings
    )


def test_event_beyond_seven_days_does_not_add_warning():
    plan = RegenerationStrategy().build(
        make_context(
            days_until_event=8,
        ),
    )

    assert (
        "An event is approaching while fatigue remains elevated."
        not in plan.warnings
    )


def test_missing_event_date_is_supported():
    plan = RegenerationStrategy().build(
        make_context(
            days_until_event=None,
        ),
    )

    assert (
        "An event is approaching while fatigue remains elevated."
        not in plan.warnings
    )


# ======================================================
# Combined recovery signals
# ======================================================


def test_combined_signals_use_most_conservative_volume():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-35.0,
            average_rpe=9.0,
            days_until_event=5,
        ),
    )

    assert plan.volume_factor == pytest.approx(0.40)
    assert plan.target_sessions == 3
    assert plan.recovery_days == 4
    assert plan.target_weekly_minutes == 180
    assert plan.target_weekly_load == pytest.approx(100.0)


def test_combined_signals_add_all_warnings():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-35.0,
            average_rpe=9.0,
            days_until_event=5,
        ),
    )

    assert plan.warnings == (
        (
            "Regeneration takes priority over planned "
            "training progression."
        ),
        "Accumulated fatigue is very high.",
        "Recent sessions have a high perceived effort.",
        (
            "An event is approaching while fatigue "
            "remains elevated."
        ),
    )


# ======================================================
# Strategy invariants
# ======================================================


@pytest.mark.parametrize(
    (
        "tsb",
        "average_rpe",
        "expected_volume",
        "expected_minutes",
        "expected_load",
    ),
    [
        (0.0, None, 0.60, 240, 150.0),
        (-30.0, 7.9, 0.60, 240, 150.0),
        (0.0, 8.0, 0.50, 240, 125.0),
        (-30.1, None, 0.40, 180, 100.0),
        (-40.0, 9.0, 0.40, 180, 100.0),
    ],
)
def test_weekly_targets_match_volume_factor(
    tsb,
    average_rpe,
    expected_volume,
    expected_minutes,
    expected_load,
):
    plan = RegenerationStrategy().build(
        make_context(
            tsb=tsb,
            average_rpe=average_rpe,
        ),
    )

    assert plan.volume_factor == pytest.approx(
        expected_volume,
    )
    assert plan.target_weekly_minutes == expected_minutes
    assert plan.target_weekly_load == pytest.approx(
        expected_load,
    )


def test_regeneration_never_prescribes_intensity():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-40.0,
            average_rpe=10.0,
            days_until_event=1,
        ),
    )

    assert plan.intensity_sessions == 0
    assert plan.has_intensity is False


def test_regeneration_never_prescribes_long_session():
    plan = RegenerationStrategy().build(
        make_context(),
    )

    assert plan.long_sessions == 0
    assert plan.long_session_minutes is None
    assert plan.has_long_session is False


def test_focus_remains_recovery_in_all_conditions():
    plan = RegenerationStrategy().build(
        make_context(
            tsb=-40.0,
            average_rpe=10.0,
            days_until_event=1,
        ),
    )

    assert plan.focus == "recovery"


def test_weekly_load_is_derived_from_volume_factor():
    plan = RegenerationStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.target_weekly_load == pytest.approx(
        250.0 * plan.volume_factor
    )


def test_repr_contains_strategy_class_and_phase():
    strategy = RegenerationStrategy()

    representation = repr(
        strategy,
    )

    assert "RegenerationStrategy" in representation
    assert "Regeneration" in representation