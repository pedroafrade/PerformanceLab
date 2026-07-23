"""
Tests for BuildStrategy.

Place this file at:
    tests/coaching/strategies/test_build_strategy.py
"""

from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.build import BuildStrategy
from performancelab.coaching.strategy import StrategyPlan


def make_context(
    *,
    tsb: float = 0.0,
    average_rpe: float | None = None,
    next_event=None,
):
    """
    Creates the minimum context required by BuildStrategy.
    """

    return SimpleNamespace(
        tsb=tsb,
        average_rpe=average_rpe,
        next_event=next_event,
    )


def make_event(
    *,
    name: str = "City Marathon",
    priority: str = "A",
):
    """
    Creates an event wrapper compatible with CoachStrategy helpers.
    """

    return SimpleNamespace(
        event=SimpleNamespace(
            name=name,
        ),
        priority=priority,
    )


# ======================================================
# Default build week
# ======================================================


def test_build_returns_strategy_plan():
    strategy = BuildStrategy()

    plan = strategy.build(
        make_context(),
    )

    assert isinstance(
        plan,
        StrategyPlan,
    )


def test_build_uses_strategy_identity():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.strategy == "BuildStrategy"
    assert plan.phase == "Build"


def test_default_build_targets():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.volume_factor == pytest.approx(1.08)
    assert plan.target_sessions == 6
    assert plan.intensity_sessions == 2
    assert plan.long_sessions == 1
    assert plan.recovery_days == 1


def test_default_build_concrete_weekly_targets():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.focus == "threshold"
    assert plan.target_weekly_minutes == 420
    assert plan.target_weekly_load == pytest.approx(540.0)
    assert plan.long_session_minutes == 120


def test_default_build_objectives():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert "Increase sustainable training load." in plan.objectives
    assert "Develop aerobic endurance." in plan.objectives
    assert "Introduce controlled intensity." in plan.objectives


def test_default_build_guidelines():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert len(plan.guidelines) == 4
    assert any(
        "Increase weekly volume gradually" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "Separate demanding sessions" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "longer endurance session" in guideline
        for guideline in plan.guidelines
    )
    assert any(
        "genuinely easy" in guideline
        for guideline in plan.guidelines
    )


def test_default_build_has_no_warnings():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.warnings == ()


# ======================================================
# Fatigue response
# ======================================================


def test_elevated_fatigue_reduces_volume_and_intensity():
    plan = BuildStrategy().build(
        make_context(
            tsb=-11.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.0)
    assert plan.intensity_sessions == 1


def test_elevated_fatigue_changes_focus():
    plan = BuildStrategy().build(
        make_context(
            tsb=-11.0,
        ),
    )

    assert plan.focus == "aerobic endurance"


def test_elevated_fatigue_adds_warning():
    plan = BuildStrategy().build(
        make_context(
            tsb=-11.0,
        ),
    )

    assert any(
        "Fatigue is elevated" in warning
        for warning in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_fatigue_reduction():
    plan = BuildStrategy().build(
        make_context(
            tsb=-10.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.08)
    assert plan.intensity_sessions == 2
    assert plan.warnings == ()


# ======================================================
# Perceived effort response
# ======================================================


def test_high_rpe_reduces_volume_and_intensity():
    plan = BuildStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.0)
    assert plan.intensity_sessions == 1


def test_high_rpe_changes_focus():
    plan = BuildStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert plan.focus == "aerobic endurance"


def test_high_rpe_adds_warning():
    plan = BuildStrategy().build(
        make_context(
            average_rpe=8.0,
        ),
    )

    assert "Recent perceived effort is high." in plan.warnings


def test_rpe_below_threshold_does_not_reduce_build():
    plan = BuildStrategy().build(
        make_context(
            average_rpe=7.9,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.08)
    assert plan.intensity_sessions == 2
    assert plan.warnings == ()


def test_missing_rpe_is_supported():
    plan = BuildStrategy().build(
        make_context(
            average_rpe=None,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.08)
    assert plan.intensity_sessions == 2


# ======================================================
# Combined fatigue signals
# ======================================================


def test_combined_fatigue_signals_keep_conservative_targets():
    plan = BuildStrategy().build(
        make_context(
            tsb=-20.0,
            average_rpe=9.0,
        ),
    )

    assert plan.volume_factor == pytest.approx(1.0)
    assert plan.intensity_sessions == 1
    assert plan.focus == "aerobic endurance"


def test_combined_fatigue_signals_add_both_warnings():
    plan = BuildStrategy().build(
        make_context(
            tsb=-20.0,
            average_rpe=9.0,
        ),
    )

    assert len(plan.warnings) == 2
    assert any(
        "Fatigue is elevated" in warning
        for warning in plan.warnings
    )
    assert "Recent perceived effort is high." in plan.warnings


def test_reduced_build_weekly_load_uses_volume_factor():
    plan = BuildStrategy().build(
        make_context(
            tsb=-20.0,
        ),
    )

    assert plan.target_weekly_load == pytest.approx(500.0)


# ======================================================
# Event preparation
# ======================================================


def test_event_adds_specific_objective():
    plan = BuildStrategy().build(
        make_context(
            next_event=make_event(
                name="Coastal Ultra",
            ),
        ),
    )

    assert (
        "Prepare progressively for Coastal Ultra."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = BuildStrategy().build(
        make_context(
            next_event=None,
        ),
    )

    assert not any(
        objective.startswith(
            "Prepare progressively for"
        )
        for objective in plan.objectives
    )


def test_event_wrapper_without_event_is_supported():
    plan = BuildStrategy().build(
        make_context(
            next_event=SimpleNamespace(
                event=None,
                priority="A",
            ),
        ),
    )

    assert not any(
        objective.startswith(
            "Prepare progressively for"
        )
        for objective in plan.objectives
    )


def test_event_without_name_is_supported():
    plan = BuildStrategy().build(
        make_context(
            next_event=SimpleNamespace(
                event=SimpleNamespace(),
                priority="A",
            ),
        ),
    )

    assert not any(
        objective.startswith(
            "Prepare progressively for"
        )
        for objective in plan.objectives
    )


# ======================================================
# Strategy invariants
# ======================================================


@pytest.mark.parametrize(
    (
        "tsb",
        "average_rpe",
        "expected_intensity",
        "expected_focus",
    ),
    [
        (0.0, None, 2, "threshold"),
        (-10.0, 7.9, 2, "threshold"),
        (-10.1, 7.9, 1, "aerobic endurance"),
        (0.0, 8.0, 1, "aerobic endurance"),
        (-20.0, 9.0, 1, "aerobic endurance"),
    ],
)
def test_focus_matches_intensity_target(
    tsb,
    average_rpe,
    expected_intensity,
    expected_focus,
):
    plan = BuildStrategy().build(
        make_context(
            tsb=tsb,
            average_rpe=average_rpe,
        ),
    )

    assert plan.intensity_sessions == expected_intensity
    assert plan.focus == expected_focus


def test_long_session_target_is_consistent():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.long_sessions == 1
    assert plan.long_session_minutes == 120
    assert (
        plan.long_session_minutes
        <= plan.target_weekly_minutes
    )


def test_weekly_load_is_derived_from_volume_factor():
    plan = BuildStrategy().build(
        make_context(),
    )

    assert plan.target_weekly_load == pytest.approx(
        500.0 * plan.volume_factor
    )


def test_repr_contains_strategy_class_and_phase():
    strategy = BuildStrategy()

    representation = repr(
        strategy,
    )

    assert "BuildStrategy" in representation
    assert "Build" in representation