from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.base import BaseStrategy


class DummyBaseStrategy(BaseStrategy):
    """Base strategy with predictable event handling for tests."""

    def __init__(self, event_name: str | None = None) -> None:
        self._test_event_name = event_name

    def _event_name(self, context) -> str | None:
        return self._test_event_name


def make_context(
    *,
    tsb: float = 0.0,
    average_rpe: float | None = None,
):
    return SimpleNamespace(
        tsb=tsb,
        average_rpe=average_rpe,
    )


def build_plan(
    *,
    tsb: float = 0.0,
    average_rpe: float | None = None,
    event_name: str | None = None,
):
    strategy = DummyBaseStrategy(
        event_name=event_name,
    )

    return strategy.build(
        make_context(
            tsb=tsb,
            average_rpe=average_rpe,
        ),
    )


# ==========================================================
# Identity
# ==========================================================


def test_base_strategy_identity():
    strategy = BaseStrategy()

    assert strategy.name == "BaseStrategy"
    assert strategy.phase == "Base"


def test_plan_contains_strategy_identity():
    plan = build_plan()

    assert plan.strategy == "BaseStrategy"
    assert plan.phase == "Base"


# ==========================================================
# Default targets
# ==========================================================


def test_default_base_targets():
    plan = build_plan()

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.target_sessions == 5
    assert plan.intensity_sessions == 1
    assert plan.long_sessions == 1
    assert plan.recovery_days == 2


def test_default_base_focus():
    plan = build_plan()

    assert plan.focus == "aerobic endurance"


def test_default_concrete_weekly_targets():
    plan = build_plan()

    assert plan.target_weekly_minutes == 360
    assert plan.target_weekly_load == pytest.approx(360.0)
    assert plan.long_session_minutes == 90


def test_weekly_load_is_derived_from_volume_factor():
    plan = build_plan()

    assert plan.target_weekly_load == pytest.approx(
        400.0 * plan.volume_factor,
    )


# ==========================================================
# Fatigue handling
# ==========================================================


def test_elevated_fatigue_reduces_volume():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.volume_factor == pytest.approx(0.80)


def test_elevated_fatigue_increases_recovery_days():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.recovery_days == 3


def test_elevated_fatigue_adds_warning():
    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        "Fatigue is elevated; prioritise recovery."
        in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_fatigue_reduction():
    plan = build_plan(
        tsb=-10.0,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.recovery_days == 2
    assert (
        "Fatigue is elevated; prioritise recovery."
        not in plan.warnings
    )


# ==========================================================
# RPE handling
# ==========================================================


def test_high_rpe_reduces_volume():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.volume_factor == pytest.approx(0.80)


def test_high_rpe_increases_recovery_days():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.recovery_days == 3


def test_high_rpe_adds_warning():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert (
        "Recent perceived effort is high."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_base():
    plan = build_plan(
        average_rpe=7.9,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.recovery_days == 2
    assert (
        "Recent perceived effort is high."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = build_plan(
        average_rpe=None,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.recovery_days == 2


# ==========================================================
# Combined fatigue signals
# ==========================================================


def test_combined_fatigue_signals_keep_conservative_targets():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.volume_factor == pytest.approx(0.80)
    assert plan.recovery_days == 3


def test_combined_fatigue_signals_add_both_warnings():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.warnings == (
        "Fatigue is elevated; prioritise recovery.",
        "Recent perceived effort is high.",
    )


def test_reduced_weekly_load_uses_volume_factor():
    plan = build_plan(
        tsb=-20.0,
    )

    assert plan.target_weekly_load == pytest.approx(320.0)


# ==========================================================
# Event objective
# ==========================================================


def test_event_adds_specific_objective():
    plan = build_plan(
        event_name="Lisbon Marathon",
    )

    assert (
        "Build a strong aerobic foundation for "
        "Lisbon Marathon."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = build_plan(
        event_name=None,
    )

    assert not any(
        objective.startswith(
            "Build a strong aerobic foundation for "
        )
        for objective in plan.objectives
    )


# ==========================================================
# Objectives and guidelines
# ==========================================================


def test_default_objectives_are_present():
    plan = build_plan()

    assert plan.objectives == (
        "Develop aerobic endurance.",
        "Build consistent training habits.",
        "Prepare for future training load.",
    )


def test_default_guidelines_are_present():
    plan = build_plan()

    assert plan.guidelines == (
        "Prioritise easy aerobic sessions.",
        "Increase training volume gradually.",
        "Include one longer endurance session.",
        "Avoid excessive high-intensity work.",
    )


def test_plan_collections_are_immutable_tuples():
    plan = build_plan()

    assert isinstance(plan.objectives, tuple)
    assert isinstance(plan.guidelines, tuple)
    assert isinstance(plan.warnings, tuple)


# ==========================================================
# Structural consistency
# ==========================================================


def test_long_session_metadata_is_consistent():
    plan = build_plan()

    assert plan.long_sessions == 1
    assert plan.long_session_minutes == 90


def test_intensity_target_remains_low_during_base_phase():
    normal_plan = build_plan()
    fatigued_plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert normal_plan.intensity_sessions == 1
    assert fatigued_plan.intensity_sessions == 1


@pytest.mark.parametrize(
    (
        "tsb",
        "average_rpe",
        "expected_volume",
        "expected_recovery_days",
    ),
    [
        (0.0, None, 0.90, 2),
        (-10.0, 7.9, 0.90, 2),
        (-10.1, 7.9, 0.80, 3),
        (0.0, 8.0, 0.80, 3),
        (-20.0, 9.0, 0.80, 3),
    ],
)
def test_base_adjustments(
    tsb,
    average_rpe,
    expected_volume,
    expected_recovery_days,
):
    plan = build_plan(
        tsb=tsb,
        average_rpe=average_rpe,
    )

    assert plan.volume_factor == pytest.approx(
        expected_volume,
    )
    assert plan.recovery_days == expected_recovery_days