"""
Tests for Coach.
"""

from datetime import date
from types import SimpleNamespace

import performancelab.coaching.coach as coach_module

from performancelab.coaching import (
    Coach,
    CoachAnalysis,
    CoachContext,
    CoachRecommendation,
)


def make_athlete(
    *,
    ctl=52.3,
    atl=48.1,
    tsb=4.2,
    next_event=None,
    days_until_event=None,
):
    """
    Creates a minimal athlete-like object for integration
    tests involving Coach.
    """

    analytics = SimpleNamespace(
        ctl=ctl,
        atl=atl,
        tsb=tsb,
        next_event=next_event,
        days_until_next_event=days_until_event,
        sports=("Running",),
        average_rpe=5.5,
        training_plan=object(),
    )

    return SimpleNamespace(
        name="Test Athlete",
        analytics=analytics,
    )


def test_recommend_returns_coach_recommendation():

    athlete = make_athlete()

    recommendation = Coach().recommend(
        athlete,
        today=date(2026, 3, 10),
    )

    assert isinstance(
        recommendation,
        CoachRecommendation,
    )


def test_recommend_builds_context_from_athlete():

    athlete = make_athlete(
        ctl=60.0,
        atl=55.0,
        tsb=5.0,
    )

    reference_date = date(2026, 3, 10)

    recommendation = Coach().recommend(
        athlete,
        today=reference_date,
    )

    assert isinstance(
        recommendation.context,
        CoachContext,
    )

    assert recommendation.context.athlete is athlete
    assert recommendation.context.today == reference_date

    assert recommendation.context.ctl == 60.0
    assert recommendation.context.atl == 55.0
    assert recommendation.context.tsb == 5.0


def test_recommend_uses_analyzer_result():

    event_entry = SimpleNamespace(
        event=SimpleNamespace(
            name="Lisbon Half Marathon",
        ),
        priority="A",
    )

    athlete = make_athlete(
        next_event=event_entry,
        days_until_event=84,
    )

    recommendation = Coach().recommend(
        athlete,
        today=date(2026, 3, 10),
    )

    assert recommendation.analysis.phase == "Build"

    assert (
        recommendation.strategy
        == "BuildStrategy"
    )

    assert recommendation.summary == (
        "Build phase for "
        "Lisbon Half Marathon."
    )


def test_recommend_propagates_warnings():

    athlete = make_athlete(
        tsb=-25.0,
    )

    recommendation = Coach().recommend(
        athlete,
        today=date(2026, 3, 10),
    )

    assert recommendation.strategy == "RecoveryStrategy"

    assert recommendation.warnings == (
        "High accumulated fatigue.",
    )


def test_recommend_orchestrates_context_and_analyzer(
    monkeypatch,
):
    """
    Tests Coach orchestration independently from the
    concrete implementations of CoachContext and
    CoachAnalyzer.
    """

    athlete = object()
    reference_date = date(2026, 3, 10)

    expected_context = object()

    expected_analysis = CoachAnalysis(
        phase="Build",
        strategy="BuildStrategy",
        warnings=("Test warning.",),
        summary="Test summary.",
    )

    calls = {}

    class FakeCoachContext:

        @classmethod
        def from_athlete(
            cls,
            received_athlete,
            today=None,
        ):
            calls["athlete"] = received_athlete
            calls["today"] = today

            return expected_context

    class FakeCoachAnalyzer:

        def __init__(
            self,
            context,
        ):
            calls["context"] = context

        def analyze(self):
            calls["analyzed"] = True

            return expected_analysis

    monkeypatch.setattr(
        coach_module,
        "CoachContext",
        FakeCoachContext,
    )

    monkeypatch.setattr(
        coach_module,
        "CoachAnalyzer",
        FakeCoachAnalyzer,
    )

    recommendation = Coach().recommend(
        athlete,
        today=reference_date,
    )

    assert calls["athlete"] is athlete
    assert calls["today"] == reference_date
    assert calls["context"] is expected_context
    assert calls["analyzed"] is True

    assert recommendation.context is expected_context
    assert recommendation.analysis is expected_analysis

    assert (
        recommendation.strategy
        == expected_analysis.strategy
    )

    assert (
        recommendation.summary
        == expected_analysis.summary
    )

    assert (
        recommendation.warnings
        == expected_analysis.warnings
    )