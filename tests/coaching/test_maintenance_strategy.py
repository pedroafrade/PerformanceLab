from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.maintenance import (
    MaintenanceStrategy,
)


class StubMaintenanceStrategy(MaintenanceStrategy):
    """Maintenance strategy with predictable event handling."""

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
    strategy = StubMaintenanceStrategy(
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


def test_maintenance_strategy_identity():
    strategy = MaintenanceStrategy()

    assert strategy.name == "MaintenanceStrategy"
    assert strategy.phase == "Maintenance"


def test_plan_contains_strategy_identity():
    plan = build_plan()

    assert plan.strategy == "MaintenanceStrategy"
    assert plan.phase == "Maintenance"


# ==========================================================
# Default targets
# ==========================================================


def test_default_maintenance_targets():
    plan = build_plan()

    assert plan.volume_factor == pytest.approx(1.00)
    assert plan.target_sessions == 5
    assert plan.intensity_sessions == 1
    assert plan.long_sessions == 1
    assert plan.recovery_days == 2


def test_default_maintenance_focus():
    plan = build_plan()

    assert plan.focus == "fitness maintenance"


def test_default_concrete_weekly_targets():
    plan = build_plan()

    assert plan.target_weekly_minutes == 360
    assert plan.target_weekly_load == pytest.approx(400.0)
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

    assert plan.volume_factor == pytest.approx(0.90)


def test_elevated_fatigue_removes_intensity():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.intensity_sessions == 0


def test_elevated_fatigue_increases_recovery_days():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.recovery_days == 3


def test_elevated_fatigue_changes_focus():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.focus == "aerobic maintenance"


def test_elevated_fatigue_adds_warning():
    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        "Fatigue is elevated; reduce training stress "
        "while maintaining consistency."
        in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_reduction():
    plan = build_plan(
        tsb=-10.0,
    )

    assert plan.volume_factor == pytest.approx(1.00)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 2
    assert plan.focus == "fitness maintenance"

    assert (
        "Fatigue is elevated; reduce training stress "
        "while maintaining consistency."
        not in plan.warnings
    )


# ==========================================================
# RPE handling
# ==========================================================


def test_high_rpe_reduces_volume():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.volume_factor == pytest.approx(0.90)


def test_high_rpe_removes_intensity():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.intensity_sessions == 0


def test_high_rpe_increases_recovery_days():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.recovery_days == 3


def test_high_rpe_changes_focus():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.focus == "aerobic maintenance"


def test_high_rpe_adds_warning():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert (
        "Recent perceived effort is high."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_maintenance():
    plan = build_plan(
        average_rpe=7.9,
    )

    assert plan.volume_factor == pytest.approx(1.00)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 2
    assert plan.focus == "fitness maintenance"

    assert (
        "Recent perceived effort is high."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = build_plan(
        average_rpe=None,
    )

    assert plan.volume_factor == pytest.approx(1.00)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 2


# ==========================================================
# Combined fatigue signals
# ==========================================================


def test_combined_fatigue_signals_keep_conservative_targets():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.intensity_sessions == 0
    assert plan.recovery_days == 3
    assert plan.focus == "aerobic maintenance"


def test_combined_fatigue_signals_add_both_warnings():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.warnings == (
        (
            "Fatigue is elevated; reduce training stress "
            "while maintaining consistency."
        ),
        "Recent perceived effort is high.",
    )


def test_reduced_weekly_load_uses_volume_factor():
    plan = build_plan(
        tsb=-20.0,
    )

    assert plan.target_weekly_load == pytest.approx(360.0)


# ==========================================================
# Event objective
# ==========================================================


def test_event_adds_specific_objective():
    plan = build_plan(
        event_name="Lisbon Marathon",
    )

    assert (
        "Maintain readiness for Lisbon Marathon."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = build_plan(
        event_name=None,
    )

    assert not any(
        objective.startswith(
            "Maintain readiness for "
        )
        for objective in plan.objectives
    )


# ==========================================================
# Objectives and guidelines
# ==========================================================


def test_default_objectives_are_present():
    plan = build_plan()

    assert plan.objectives == (
        "Maintain current aerobic fitness.",
        "Preserve training consistency.",
        "Balance quality training with recovery.",
    )


def test_default_guidelines_are_present():
    plan = build_plan()

    assert plan.guidelines == (
        "Keep weekly training volume stable.",
        "Include controlled intensity without progression.",
        "Maintain one longer aerobic session.",
        "Avoid unnecessary increases in training load.",
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


def test_intensity_is_removed_only_for_fatigue_signals():
    normal_plan = build_plan()
    fatigued_plan = build_plan(
        tsb=-20.0,
    )
    high_rpe_plan = build_plan(
        average_rpe=9.0,
    )

    assert normal_plan.intensity_sessions == 1
    assert fatigued_plan.intensity_sessions == 0
    assert high_rpe_plan.intensity_sessions == 0


@pytest.mark.parametrize(
    (
        "tsb",
        "average_rpe",
        "expected_volume",
        "expected_intensity",
        "expected_recovery_days",
        "expected_focus",
    ),
    [
        (
            0.0,
            None,
            1.00,
            1,
            2,
            "fitness maintenance",
        ),
        (
            -10.0,
            7.9,
            1.00,
            1,
            2,
            "fitness maintenance",
        ),
        (
            -10.1,
            7.9,
            0.90,
            0,
            3,
            "aerobic maintenance",
        ),
        (
            0.0,
            8.0,
            0.90,
            0,
            3,
            "aerobic maintenance",
        ),
        (
            -20.0,
            9.0,
            0.90,
            0,
            3,
            "aerobic maintenance",
        ),
    ],
)
def test_maintenance_adjustments(
    tsb,
    average_rpe,
    expected_volume,
    expected_intensity,
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
    assert plan.intensity_sessions == expected_intensity
    assert plan.recovery_days == expected_recovery_days
    assert plan.focus == expected_focus