from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.taper import (
    TaperStrategy,
)


class StubTaperStrategy(TaperStrategy):
    """Taper strategy with predictable event handling."""

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
    strategy = StubTaperStrategy(
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


def test_taper_strategy_identity():
    strategy = TaperStrategy()

    assert strategy.name == "TaperStrategy"
    assert strategy.phase == "Taper"


def test_plan_contains_strategy_identity():
    plan = build_plan()

    assert plan.strategy == "TaperStrategy"
    assert plan.phase == "Taper"


# ==========================================================
# Default targets
# ==========================================================


def test_default_taper_targets():
    plan = build_plan()

    assert plan.volume_factor == pytest.approx(0.65)
    assert plan.target_sessions == 4
    assert plan.intensity_sessions == 1
    assert plan.long_sessions == 0
    assert plan.recovery_days == 3


def test_default_taper_focus():
    plan = build_plan()

    assert plan.focus == "race readiness"


def test_default_concrete_weekly_targets():
    plan = build_plan()

    assert plan.target_weekly_minutes == 240
    assert plan.target_weekly_load == pytest.approx(227.5)
    assert plan.long_session_minutes is None


def test_weekly_load_is_derived_from_volume_factor():
    plan = build_plan()

    assert plan.target_weekly_load == pytest.approx(
        350.0 * plan.volume_factor,
    )


# ==========================================================
# Fatigue handling
# ==========================================================


def test_elevated_fatigue_reduces_volume():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.volume_factor == pytest.approx(0.50)


def test_elevated_fatigue_removes_intensity():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.intensity_sessions == 0


def test_elevated_fatigue_increases_recovery_days():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.recovery_days == 4


def test_elevated_fatigue_changes_focus():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.focus == "fatigue reduction"


def test_elevated_fatigue_adds_warning():
    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        "Fatigue remains elevated; prioritise recovery "
        "over additional race-specific work."
        in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_reduction():
    plan = build_plan(
        tsb=-10.0,
    )

    assert plan.volume_factor == pytest.approx(0.65)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 3
    assert plan.focus == "race readiness"

    assert (
        "Fatigue remains elevated; prioritise recovery "
        "over additional race-specific work."
        not in plan.warnings
    )


# ==========================================================
# RPE handling
# ==========================================================


def test_high_rpe_reduces_volume():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.volume_factor == pytest.approx(0.50)


def test_high_rpe_removes_intensity():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.intensity_sessions == 0


def test_high_rpe_increases_recovery_days():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.recovery_days == 4


def test_high_rpe_changes_focus():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.focus == "fatigue reduction"


def test_high_rpe_adds_warning():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert (
        "Recent perceived effort is high."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_taper():
    plan = build_plan(
        average_rpe=7.9,
    )

    assert plan.volume_factor == pytest.approx(0.65)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 3
    assert plan.focus == "race readiness"

    assert (
        "Recent perceived effort is high."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = build_plan(
        average_rpe=None,
    )

    assert plan.volume_factor == pytest.approx(0.65)
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 3


# ==========================================================
# Combined fatigue signals
# ==========================================================


def test_combined_fatigue_signals_keep_conservative_targets():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.volume_factor == pytest.approx(0.50)
    assert plan.intensity_sessions == 0
    assert plan.recovery_days == 4
    assert plan.focus == "fatigue reduction"


def test_combined_fatigue_signals_add_both_warnings():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.warnings == (
        (
            "Fatigue remains elevated; prioritise recovery "
            "over additional race-specific work."
        ),
        "Recent perceived effort is high.",
    )


def test_reduced_weekly_load_uses_volume_factor():
    plan = build_plan(
        tsb=-20.0,
    )

    assert plan.target_weekly_load == pytest.approx(175.0)


# ==========================================================
# Event objective
# ==========================================================


def test_event_adds_specific_objective():
    plan = build_plan(
        event_name="Lisbon Marathon",
    )

    assert (
        "Arrive rested and prepared for Lisbon Marathon."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = build_plan(
        event_name=None,
    )

    assert not any(
        objective.startswith(
            "Arrive rested and prepared for "
        )
        for objective in plan.objectives
    )


# ==========================================================
# Objectives and guidelines
# ==========================================================


def test_default_objectives_are_present():
    plan = build_plan()

    assert plan.objectives == (
        "Reduce accumulated fatigue.",
        "Preserve race-specific sharpness.",
        "Improve readiness for competition.",
    )


def test_default_guidelines_are_present():
    plan = build_plan()

    assert plan.guidelines == (
        "Reduce training volume substantially.",
        "Keep intensity brief and controlled.",
        "Avoid introducing new training stress.",
        "Prioritise recovery, sleep, and consistency.",
    )


def test_plan_collections_are_immutable_tuples():
    plan = build_plan()

    assert isinstance(plan.objectives, tuple)
    assert isinstance(plan.guidelines, tuple)
    assert isinstance(plan.warnings, tuple)


# ==========================================================
# Structural consistency
# ==========================================================


def test_taper_has_no_long_session():
    plan = build_plan()

    assert plan.long_sessions == 0
    assert plan.long_session_minutes is None


def test_intensity_removed_only_when_required():
    normal = build_plan()
    fatigued = build_plan(
        tsb=-20.0,
    )

    assert normal.intensity_sessions == 1
    assert fatigued.intensity_sessions == 0


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
            0.65,
            1,
            3,
            "race readiness",
        ),
        (
            -10.0,
            7.9,
            0.65,
            1,
            3,
            "race readiness",
        ),
        (
            -10.1,
            7.9,
            0.50,
            0,
            4,
            "fatigue reduction",
        ),
        (
            0.0,
            8.0,
            0.50,
            0,
            4,
            "fatigue reduction",
        ),
        (
            -20.0,
            9.0,
            0.50,
            0,
            4,
            "fatigue reduction",
        ),
    ],
)
def test_taper_adjustments(
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