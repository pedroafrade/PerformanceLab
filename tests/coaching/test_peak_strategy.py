from types import SimpleNamespace

import pytest

from performancelab.coaching.strategies.peak import (
    PeakStrategy,
)


class StubPeakStrategy(PeakStrategy):
    """Peak strategy with predictable event handling."""

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
    phase_event=None,
    primary_event=None,
    days_until_phase_event: int | None = None,
    typical_running_long_session_elevation_gain: float = 0.0,
):
    return SimpleNamespace(
        tsb=tsb,
        average_rpe=average_rpe,
        next_event=phase_event,
        phase_event=phase_event,
        primary_event=primary_event,
        training_state=SimpleNamespace(
            typical_running_long_session_elevation_gain=(
                typical_running_long_session_elevation_gain
            ),
        ),
        days_until_phase_event=(
            days_until_phase_event
        ),
    )

def build_plan(
    *,
    tsb: float = 0.0,
    average_rpe: float | None = None,
    event_name: str | None = None,
    phase_event=None,
    primary_event=None,
    days_until_phase_event: int | None = None,
    typical_running_long_session_elevation_gain: float = 0.0,
):
    strategy = StubPeakStrategy(
        event_name=event_name,
    )

    return strategy.build(
        make_context(
            tsb=tsb,
            average_rpe=average_rpe,
            phase_event=phase_event,
            primary_event=primary_event,
            typical_running_long_session_elevation_gain=(
                typical_running_long_session_elevation_gain
            ),
            days_until_phase_event=(
                days_until_phase_event
            ),
        ),
    )


# ==========================================================
# Identity
# ==========================================================


def test_peak_strategy_identity():
    strategy = PeakStrategy()

    assert strategy.name == "PeakStrategy"
    assert strategy.phase == "Peak"


def test_plan_contains_strategy_identity():
    plan = build_plan()

    assert plan.strategy == "PeakStrategy"
    assert plan.phase == "Peak"


# ==========================================================
# Default targets
# ==========================================================


def test_default_peak_targets():
    plan = build_plan()

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.target_sessions == 5
    assert plan.intensity_sessions == 2
    assert plan.long_sessions == 1
    assert plan.recovery_days == 2


def test_default_peak_focus():
    plan = build_plan()

    assert plan.focus == "race-specific intensity"

def test_default_peak_uses_concrete_key_session():

    plan = build_plan()

    assert (
        plan.key_session_focus
        == "threshold"
    )


def test_trail_peak_rotates_key_session_focus():

    event = SimpleNamespace(
        event=SimpleNamespace(
            name="Trail Race",
            sport="Trail Running",
        ),
    )

    focuses = tuple(
        build_plan(
            phase_event=event,
            days_until_phase_event=days,
        ).key_session_focus
        for days in (
            28,
            35,
            42,
        )
    )

    assert set(focuses) == {
        "hills",
        "threshold",
        "tempo",
    }

def test_trail_peak_preserves_elevation_demand():

    event = SimpleNamespace(
        event=SimpleNamespace(
            name="Trail Race",
            sport="Trail Running",
            elevation_demand="mountainous",
        ),
    )

    plan = build_plan(
        phase_event=event,
    )

    assert (
        plan.elevation_demand
        == "mountainous"
    )
    
def test_trail_peak_progresses_long_elevation():

    event = SimpleNamespace(
        event=SimpleNamespace(
            name="Trail Race",
            sport="Trail Running",
            elevation_demand="mountainous",
            elevation_gain=950,
        ),
    )

    targets = tuple(
        build_plan(
            phase_event=event,
            days_until_phase_event=days,
            typical_running_long_session_elevation_gain=(
                175
            ),
        ).long_session_elevation_gain
        for days in (
            36,
            29,
        )
    )

    assert targets == (
        475,
        575,
    )

def test_road_peak_uses_vo2max_sparingly():

    event = SimpleNamespace(
        event=SimpleNamespace(
            name="Road Race",
            sport="Road Running",
        ),
    )

    focuses = tuple(
        build_plan(
            phase_event=event,
            days_until_phase_event=days,
        ).key_session_focus
        for days in (
            21,
            28,
            35,
            42,
        )
    )

    assert focuses.count(
        "vo2max"
    ) == 1


def test_fatigue_uses_controlled_tempo_focus():

    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        plan.key_session_focus
        == "tempo"
    )

def test_default_concrete_weekly_targets():
    plan = build_plan()

    assert plan.target_weekly_minutes == 330
    assert plan.target_weekly_load == pytest.approx(405.0)
    assert plan.long_session_minutes == 90


def test_weekly_load_is_derived_from_volume_factor():
    plan = build_plan()

    assert plan.target_weekly_load == pytest.approx(
        450.0 * plan.volume_factor,
    )


# ==========================================================
# Fatigue handling
# ==========================================================


def test_elevated_fatigue_reduces_volume():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.volume_factor == pytest.approx(0.80)


def test_elevated_fatigue_reduces_intensity():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.intensity_sessions == 1


def test_elevated_fatigue_increases_recovery_days():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.recovery_days == 3


def test_elevated_fatigue_changes_focus():
    plan = build_plan(
        tsb=-10.1,
    )

    assert plan.focus == "race-specific endurance"


def test_elevated_fatigue_adds_warning():
    plan = build_plan(
        tsb=-10.1,
    )

    assert (
        "Fatigue is elevated; reduce training stress "
        "without removing all race-specific work."
        in plan.warnings
    )


def test_tsb_boundary_does_not_trigger_reduction():
    plan = build_plan(
        tsb=-10.0,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.intensity_sessions == 2
    assert plan.recovery_days == 2
    assert plan.focus == "race-specific intensity"

    assert (
        "Fatigue is elevated; reduce training stress "
        "without removing all race-specific work."
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


def test_high_rpe_reduces_intensity():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.intensity_sessions == 1


def test_high_rpe_increases_recovery_days():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.recovery_days == 3


def test_high_rpe_changes_focus():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert plan.focus == "race-specific endurance"


def test_high_rpe_adds_warning():
    plan = build_plan(
        average_rpe=8.0,
    )

    assert (
        "Recent perceived effort is high."
        in plan.warnings
    )


def test_rpe_below_threshold_does_not_reduce_peak():
    plan = build_plan(
        average_rpe=7.9,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.intensity_sessions == 2
    assert plan.recovery_days == 2
    assert plan.focus == "race-specific intensity"

    assert (
        "Recent perceived effort is high."
        not in plan.warnings
    )


def test_missing_rpe_is_supported():
    plan = build_plan(
        average_rpe=None,
    )

    assert plan.volume_factor == pytest.approx(0.90)
    assert plan.intensity_sessions == 2
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
    assert plan.intensity_sessions == 1
    assert plan.recovery_days == 3
    assert plan.focus == "race-specific endurance"


def test_combined_fatigue_signals_add_both_warnings():
    plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert plan.warnings == (
        (
            "Fatigue is elevated; reduce training stress "
            "without removing all race-specific work."
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
        "Sharpen readiness for Lisbon Marathon."
        in plan.objectives
    )


def test_missing_event_does_not_add_event_objective():
    plan = build_plan(
        event_name=None,
    )

    assert not any(
        objective.startswith(
            "Sharpen readiness for "
        )
        for objective in plan.objectives
    )


# ==========================================================
# Objectives and guidelines
# ==========================================================


def test_default_objectives_are_present():
    plan = build_plan()

    assert plan.objectives == (
        "Sharpen race-specific fitness.",
        "Preserve intensity while reducing excess volume.",
        "Improve readiness for peak performance.",
    )


def test_default_guidelines_are_present():
    plan = build_plan()

    assert plan.guidelines == (
        "Prioritise quality over training volume.",
        "Keep demanding sessions controlled and specific.",
        "Maintain one reduced long endurance session.",
        "Allow sufficient recovery between key sessions.",
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


def test_peak_keeps_some_intensity_under_fatigue():
    normal_plan = build_plan()
    fatigued_plan = build_plan(
        tsb=-20.0,
        average_rpe=9.0,
    )

    assert normal_plan.intensity_sessions == 2
    assert fatigued_plan.intensity_sessions == 1


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
            0.90,
            2,
            2,
            "race-specific intensity",
        ),
        (
            -10.0,
            7.9,
            0.90,
            2,
            2,
            "race-specific intensity",
        ),
        (
            -10.1,
            7.9,
            0.80,
            1,
            3,
            "race-specific endurance",
        ),
        (
            0.0,
            8.0,
            0.80,
            1,
            3,
            "race-specific endurance",
        ),
        (
            -20.0,
            9.0,
            0.80,
            1,
            3,
            "race-specific endurance",
        ),
    ],
)
def test_peak_adjustments(
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