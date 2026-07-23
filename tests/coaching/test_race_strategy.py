from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.race import (
    RaceStrategy,
)


class StubRaceStrategy(RaceStrategy):
    """Race strategy with predictable event handling."""

    def __init__(
        self,
        event_name: str | None = None,
    ) -> None:
        self._test_event_name = event_name

    def _event_name(
        self,
        context,
    ) -> str | None:
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
    strategy = StubRaceStrategy(
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


def test_race_strategy_identity():
    strategy = RaceStrategy()

    assert strategy.name == "RaceStrategy"
    assert strategy.phase == "Race"


def test_plan_contains_strategy_identity():
    plan = build_plan()

    assert plan.strategy == "RaceStrategy"
    assert plan.phase == "Race"


# ==========================================================
# Default targets
# ==========================================================


def test_default_race_targets():
    plan = build_plan()

    assert plan.volume_factor == pytest.approx(0.40)
    assert plan.target_sessions == 3
    assert plan.intensity_sessions == 0
    assert plan.long_sessions == 0
    assert plan.recovery_days == 4


def test_default_race_focus():
    plan = build_plan()

    assert plan.focus == "competition"


def test_default_concrete_weekly_targets():
    plan = build_plan()

    assert plan.target_weekly_minutes == 150
    assert plan.target_weekly_load == pytest.approx(100.0)
    assert plan.long_session_minutes is None


def test_weekly_load_is_derived_from_volume_factor():
    plan = build_plan()

    assert plan.target_weekly_load == pytest.approx(
        250.0 * plan.volume_factor,
    )


# ==========================================================
# Fatigue handling
# ==========================================================


def test_elevated_fatigue_reduces_volume():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.volume_factor == pytest.approx(0.30)


def test_elevated_fatigue_reduces_target_sessions():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.target_sessions == 2


def test_elevated_fatigue_increases_recovery_days():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.recovery_days == 5


def test_elevated_fatigue_changes_focus():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.focus == "race recovery and readiness"


def test_elevated_fatigue_adds_warning():
    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        "Fatigue is elevated during race week; "
        "remove all unnecessary training stress."
        in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_reduction():
    plan = build_plan(
        tsb=-10.0,
    )

    assert plan.volume_factor == pytest.approx(0.40)
    assert plan.target_sessions == 3
    assert plan.recovery_days == 4
    assert plan.focus == "competition"

    assert (
        "Fatigue is elevated during race week; "
        "remove all unnecessary training stress."
        not in plan.warnings
    )


# ==========================================================
# RPE handling
# ==========================================================


def test_high_rpe_reduces_volume():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.volume_factor == pytest.approx(0.30)


def test_high_rpe_reduces_target_sessions():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.target_sessions == 2


def test_high_rpe_increases_recovery_days():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.recovery_days == 5


def test_high_rpe_changes_focus():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.focus == "race recovery and readiness"


def test_high_rpe_adds_warning():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert (
        "Recent perceived effort is high."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_race():
    plan = build_plan(
        average_rpe=7.9,
    )

    assert plan.volume_factor == pytest.approx(0.40)
    assert plan.target_sessions == 3
    assert plan.recovery_days == 4
    assert plan.focus == "competition"

    assert (
        "Recent perceived effort is high."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = build_plan(
        average_rpe=None,
    )

    assert plan.volume_factor == pytest.approx(0.40)
    assert plan.target_sessions == 3
    assert plan.recovery_days == 4


# ==========================================================
# Combined fatigue signals
# ==========================================================


def test_combined_fatigue_signals_keep_conservative_targets():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.volume_factor == pytest.approx(0.30)
    assert plan.target_sessions == 2
    assert plan.intensity_sessions == 0
    assert plan.long_sessions == 0
    assert plan.recovery_days == 5
    assert plan.focus == "race recovery and readiness"


def test_combined_fatigue_signals_add_both_warnings():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.warnings == (
        (
            "Fatigue is elevated during race week; "
            "remove all unnecessary training stress."
        ),
        "Recent perceived effort is high.",
    )


def test_reduced_weekly_load_uses_volume_factor():
    plan = build_plan(
        tsb=-20.0,
    )

    assert plan.target_weekly_load == pytest.approx(75.0)


# ==========================================================
# Event objective
# ==========================================================


def test_event_adds_specific_objective():
    plan = build_plan(
        event_name="Lisbon Marathon",
    )

    assert (
        "Perform effectively at Lisbon Marathon."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = build_plan(
        event_name=None,
    )

    assert not any(
        objective.startswith(
            "Perform effectively at "
        )
        for objective in plan.objectives
    )


# ==========================================================
# Objectives and guidelines
# ==========================================================


def test_default_objectives_are_present():
    plan = build_plan()

    assert plan.objectives == (
        "Arrive at competition rested and prepared.",
        "Preserve physical and mental readiness.",
        "Execute the planned race strategy.",
    )


def test_default_guidelines_are_present():
    plan = build_plan()

    assert plan.guidelines == (
        "Keep all non-race training short and easy.",
        "Avoid introducing new training stress.",
        "Prioritise sleep, hydration, and nutrition.",
        "Treat the race as the primary weekly load.",
    )


def test_plan_collections_are_immutable_tuples():
    plan = build_plan()

    assert isinstance(plan.objectives, tuple)
    assert isinstance(plan.guidelines, tuple)
    assert isinstance(plan.warnings, tuple)


# ==========================================================
# Structural consistency
# ==========================================================


def test_race_plan_has_no_training_intensity_session():
    plan = build_plan()

    assert plan.intensity_sessions == 0


def test_race_plan_has_no_long_session():
    plan = build_plan()

    assert plan.long_sessions == 0
    assert plan.long_session_minutes is None


def test_fatigue_reduces_sessions_but_keeps_race_week_valid():
    normal = build_plan()
    fatigued = build_plan(
        tsb=-20.0,
    )

    assert normal.target_sessions == 3
    assert fatigued.target_sessions == 2
    assert fatigued.recovery_days == 5


@pytest.mark.parametrize(
    (
        "tsb",
        "average_rpe",
        "expected_volume",
        "expected_sessions",
        "expected_recovery_days",
        "expected_focus",
    ),
    [
        (
            0.0,
            None,
            0.40,
            3,
            4,
            "competition",
        ),
        (
            -10.0,
            7.9,
            0.40,
            3,
            4,
            "competition",
        ),
        (
            -10.1,
            7.9,
            0.30,
            2,
            5,
            "race recovery and readiness",
        ),
        (
            0.0,
            8.0,
            0.30,
            2,
            5,
            "race recovery and readiness",
        ),
        (
            -20.0,
            9.0,
            0.30,
            2,
            5,
            "race recovery and readiness",
        ),
    ],
)
def test_race_adjustments(
    tsb,
    average_rpe,
    expected_volume,
    expected_sessions,
    expected_recovery_days,
    expected_focus,
):
    plan = build_plan(
        tsb=tsb,
        average_rpe=average_rpe,
    )

    assert plan.volume_factor == pytest.approx(
        expected_volume,
    )
    assert plan.target_sessions == expected_sessions
    assert plan.intensity_sessions == 0
    assert plan.long_sessions == 0
    assert plan.recovery_days == expected_recovery_days
    assert plan.focus == expected_focus