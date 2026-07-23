"""
Tests for CoachRecommendation.
"""

from datetime import date
from types import SimpleNamespace

import pytest

from performancelab.coaching import (
    CoachAnalysis,
    CoachContext,
    CoachRecommendation,
)


def make_context():

    return CoachContext(
        athlete=SimpleNamespace(
            name="Test Athlete",
        ),
        today=date(2026, 3, 10),
        ctl=52.0,
        atl=48.0,
        tsb=4.0,
        next_event=None,
        days_until_event=None,
        sports=("Running",),
        average_rpe=5.5,
        training_plan=object(),
    )


def make_analysis():

    return CoachAnalysis(
        phase="Base",
        strategy="BaseStrategy",
        warnings=(),
        summary=(
            "No upcoming event. "
            "Focus on general fitness."
        ),
    )


def test_recommendation_stores_context_and_analysis():

    context = make_context()
    analysis = make_analysis()

    recommendation = CoachRecommendation(
        context=context,
        analysis=analysis,
        strategy=analysis.strategy,
        summary=analysis.summary,
    )

    assert recommendation.context is context
    assert recommendation.analysis is analysis


def test_recommendation_stores_strategy_and_summary():

    context = make_context()
    analysis = make_analysis()

    recommendation = CoachRecommendation(
        context=context,
        analysis=analysis,
        strategy="BaseStrategy",
        summary="General fitness week.",
    )

    assert recommendation.strategy == "BaseStrategy"
    assert recommendation.summary == "General fitness week."


def test_recommendation_has_empty_warnings_by_default():

    recommendation = CoachRecommendation(
        context=make_context(),
        analysis=make_analysis(),
        strategy="BaseStrategy",
        summary="General fitness week.",
    )

    assert recommendation.warnings == ()


def test_recommendation_accepts_warnings():

    warnings = (
        "High accumulated fatigue.",
        "Reduce training intensity.",
    )

    recommendation = CoachRecommendation(
        context=make_context(),
        analysis=make_analysis(),
        strategy="RegenerationStrategy",
        summary="Regeneration week.",
        warnings=warnings,
    )

    assert recommendation.warnings == warnings


def test_recommendation_is_immutable():

    recommendation = CoachRecommendation(
        context=make_context(),
        analysis=make_analysis(),
        strategy="BaseStrategy",
        summary="General fitness week.",
    )

    with pytest.raises(
        AttributeError,
    ):
        recommendation.strategy = "BuildStrategy"