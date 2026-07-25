"""
Tests for CoachAnalyzer.
"""

from datetime import date
from types import SimpleNamespace

import pytest

from performancelab.coaching import (
    CoachAnalysis,
    CoachAnalyzer,
    CoachContext,
)


def make_context(
    *,
    days_until_event=None,
    days_since_event=None,
    tsb=0.0,
    ctl=50.0,
    atl=50.0,
    next_event=None,
    previous_event=None,
    upcoming_events=(),
):
    """
    Creates a CoachContext suitable for analyzer tests.
    """

    if (
        next_event is None
        and days_until_event is not None
    ):
        next_event = SimpleNamespace(
            event=SimpleNamespace(
                name="Test Race",
            ),
            priority="A",
        )

    if (
        previous_event is None
        and days_since_event is not None
    ):
        previous_event = SimpleNamespace(
            event=SimpleNamespace(
                name="Previous Race",
            ),
            priority="A",
        )

    athlete = SimpleNamespace(
        name="Test Athlete",
    )

    return CoachContext(
        athlete=athlete,
        today=date(
            2026,
            3,
            10,
        ),
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        next_event=next_event,
        days_until_event=days_until_event,
        previous_event=previous_event,
        days_since_event=days_since_event,
        upcoming_events=upcoming_events,
        sports=("Running",),
        average_rpe=5.0,
        training_plan=object(),
    )

def test_analyze_returns_coach_analysis():

    context = make_context()

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert isinstance(
        analysis,
        CoachAnalysis,
    )


def test_no_event_returns_maintenance_phase():

    context = make_context(
        next_event=None,
        days_until_event=None,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Maintenance"
    assert analysis.strategy == "MaintenanceStrategy"

    assert analysis.summary == (
        "No upcoming event. "
        "Focus on general fitness."
    )


@pytest.mark.parametrize(
    "days_until_event",
    [
        85,
        120,
        365,
    ],
)
def test_event_more_than_twelve_weeks_away_returns_base_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Base"
    assert analysis.strategy == "BaseStrategy"


@pytest.mark.parametrize(
    "days_until_event",
    [
        43,
        56,
        84,
    ],
)
def test_event_between_six_and_twelve_weeks_returns_build_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Build"
    assert analysis.strategy == "BuildStrategy"


@pytest.mark.parametrize(
    "days_until_event",
    [
        15,
        21,
        42,
    ],
)
def test_event_between_two_and_six_weeks_returns_peak_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Peak"
    assert analysis.strategy == "PeakStrategy"


@pytest.mark.parametrize(
    "days_until_event",
    [
        8,
        10,
        14,
    ],
)
def test_event_between_eight_and_fourteen_days_returns_taper_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Taper"
    assert analysis.strategy == "TaperStrategy"


@pytest.mark.parametrize(
    "days_until_event",
    [
        0,
        1,
        7,
    ],
)
def test_event_within_race_week_returns_race_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Race"
    assert analysis.strategy == "RaceStrategy"


@pytest.mark.parametrize(
    "days_until_event",
    [
        -1,
        -7,
        -30,
    ],
)
def test_past_event_returns_regeneration_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Regeneration"
    assert analysis.strategy == "RegenerationStrategy"


def test_phase_boundary_at_84_days_is_build():

    context = make_context(
        days_until_event=84,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Build"


def test_phase_boundary_at_85_days_is_base():

    context = make_context(
        days_until_event=85,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Base"


def test_phase_boundary_at_42_days_is_peak():

    context = make_context(
        days_until_event=42,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Peak"


def test_phase_boundary_at_43_days_is_build():

    context = make_context(
        days_until_event=43,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Build"


def test_phase_boundary_at_14_days_is_taper():

    context = make_context(
        days_until_event=14,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Taper"


def test_phase_boundary_at_15_days_is_peak():

    context = make_context(
        days_until_event=15,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Peak"


def test_phase_boundary_at_7_days_is_race():

    context = make_context(
        days_until_event=7,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Race"


def test_phase_boundary_at_8_days_is_taper():

    context = make_context(
        days_until_event=8,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Taper"


def test_phase_boundary_at_zero_days_is_race():

    context = make_context(
        days_until_event=0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Race"


def test_phase_boundary_at_minus_one_day_is_regeneration():

    context = make_context(
        days_until_event=-1,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Regeneration"


def test_negative_tsb_selects_regeneration_strategy():

    context = make_context(
        days_until_event=84,
        tsb=-21.0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Build"

    assert (
        analysis.strategy
        == "RegenerationStrategy"
    )


def test_tsb_equal_to_minus_twenty_does_not_select_regeneration():

    context = make_context(
        days_until_event=84,
        tsb=-20.0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.strategy == "BuildStrategy"


def test_high_fatigue_generates_warning():

    context = make_context(
        tsb=-25.0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.warnings == (
        "High accumulated fatigue.",
    )


def test_normal_tsb_does_not_generate_warning():

    context = make_context(
        tsb=5.0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.warnings == ()


def test_summary_contains_phase_and_event_name():

    event_entry = SimpleNamespace(
        event=SimpleNamespace(
            name="Lisbon Half Marathon",
        ),
        priority="A",
    )

    context = make_context(
        next_event=event_entry,
        days_until_event=84,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.summary == (
        "Build phase for "
        "Lisbon Half Marathon."
    )


def test_regeneration_strategy_preserves_original_phase():

    context = make_context(
        days_until_event=30,
        tsb=-30.0,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Peak"

    assert (
        analysis.strategy
        == "RegenerationStrategy"
    )

@pytest.mark.parametrize(
    "days_since_event",
    [
        0,
        1,
        3,
        7,
    ],
)
def test_recent_event_returns_regeneration_phase(
    days_since_event,
):
    context = make_context(
        days_since_event=days_since_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Regeneration"
    assert (
        analysis.strategy
        == "RegenerationStrategy"
    )


def test_event_eight_days_ago_does_not_force_regeneration():
    context = make_context(
        days_since_event=8,
        days_until_event=85,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Base"
    assert analysis.strategy == "BaseStrategy"


def test_recent_event_takes_priority_over_upcoming_event():
    context = make_context(
        days_since_event=2,
        days_until_event=30,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Regeneration"
    assert (
        analysis.strategy
        == "RegenerationStrategy"
    )


def test_no_previous_event_uses_normal_event_cycle():
    context = make_context(
        previous_event=None,
        days_since_event=None,
        days_until_event=30,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Peak"
    assert analysis.strategy == "PeakStrategy"