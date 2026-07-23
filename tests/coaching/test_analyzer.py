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
    tsb=0.0,
    ctl=50.0,
    atl=50.0,
    next_event=None,
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

    athlete = SimpleNamespace(
        name="Test Athlete",
    )

    return CoachContext(
        athlete=athlete,
        today=date(2026, 3, 10),
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        next_event=next_event,
        days_until_event=days_until_event,
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


def test_no_event_returns_base_phase():

    context = make_context(
        next_event=None,
        days_until_event=None,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Base"
    assert analysis.strategy == "BaseStrategy"

    assert analysis.summary == (
        "No upcoming event. "
        "Focus on general fitness."
    )


@pytest.mark.parametrize(
    "days_until_event",
    [
        57,
        84,
        120,
        365,
    ],
)
def test_event_more_than_eight_weeks_away_returns_build_phase(
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
        22,
        28,
        42,
        56,
    ],
)
def test_event_between_three_and_eight_weeks_returns_specific_phase(
    days_until_event,
):

    context = make_context(
        days_until_event=days_until_event,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Specific"

    assert (
        analysis.strategy
        == "SpecificStrategy"
    )


@pytest.mark.parametrize(
    "days_until_event",
    [
        0,
        1,
        7,
        14,
        21,
    ],
)
def test_event_within_three_weeks_returns_taper_phase(
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


def test_phase_boundary_at_56_days_is_specific():

    context = make_context(
        days_until_event=56,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Specific"


def test_phase_boundary_at_57_days_is_build():

    context = make_context(
        days_until_event=57,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Build"


def test_phase_boundary_at_21_days_is_taper():

    context = make_context(
        days_until_event=21,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Taper"


def test_phase_boundary_at_22_days_is_specific():

    context = make_context(
        days_until_event=22,
    )

    analysis = CoachAnalyzer(
        context,
    ).analyze()

    assert analysis.phase == "Specific"


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

    assert analysis.phase == "Specific"

    assert (
        analysis.strategy
        == "RegenerationStrategy"
    )