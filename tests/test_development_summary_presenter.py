"""
Tests for historical development summary cards.
"""

from performancelab.presentation import (
    DevelopmentSummaryPresenter,
    DevelopmentTrendMetricData,
    DevelopmentTrendsData,
)


def metric(
    *,
    current,
    previous,
    percentage,
    current_samples=2,
    previous_samples=1,
):
    return DevelopmentTrendMetricData(
        current_value=current,
        previous_value=previous,
        absolute_change=(
            current - previous
            if (
                current is not None
                and previous is not None
            )
            else None
        ),
        percentage_change=percentage,
        improvement_percentage=percentage,
        current_samples=current_samples,
        previous_samples=previous_samples,
        window_days=28,
    )


def create_trends():

    return DevelopmentTrendsData(
        exercise_minutes_per_day=(
            metric(
                current=42.5,
                previous=35.0,
                percentage=21.4,
            )
        ),
        exercise_distance_per_day=(
            metric(
                current=5.0,
                previous=4.0,
                percentage=25.0,
            )
        ),
        running_pace_per_kilometre=(
            metric(
                current=5.2,
                previous=5.5,
                percentage=-5.5,
            )
        ),
        active_calories_per_day=(
            metric(
                current=320.0,
                previous=280.0,
                percentage=14.3,
            )
        ),
        vo2max=(
            metric(
                current=52.4,
                previous=50.0,
                percentage=4.8,
                current_samples=1,
            )
        ),
    )


def test_builds_four_historical_summary_cards():

    cards = (
        DevelopmentSummaryPresenter(
            create_trends()
        ).build()
    )

    assert len(cards) == 4

    assert [
        card.key
        for card in cards
    ] == [
        "exercise-time",
        "running-pace",
        "active-calories",
        "vo2max",
    ]


def test_formats_historical_summary_values():

    cards = (
        DevelopmentSummaryPresenter(
            create_trends()
        ).build()
    )

    assert cards[0].value == (
        "42.5 min/day"
    )
    assert cards[1].value == (
        "5:12 min/km"
    )
    assert cards[2].value == (
        "320 active kcal/day"
    )
    assert cards[3].value == (
        "52.4 ml/kg/min"
    )


def test_describes_direction_without_judgement():

    cards = (
        DevelopmentSummaryPresenter(
            create_trends()
        ).build()
    )

    assert cards[0].trend == "↑ 21.4%"
    assert cards[1].trend == "↓ 5.5%"
    assert cards[3].trend == "↑ 4.8%"


def test_formats_missing_values():

    missing = metric(
        current=None,
        previous=None,
        percentage=None,
        current_samples=0,
        previous_samples=0,
    )

    trends = DevelopmentTrendsData(
        exercise_minutes_per_day=missing,
        exercise_distance_per_day=missing,
        running_pace_per_kilometre=missing,
        active_calories_per_day=missing,
        vo2max=missing,
    )

    cards = (
        DevelopmentSummaryPresenter(
            trends
        ).build()
    )

    assert all(
        card.value == "—"
        for card in cards
    )

    assert all(
        card.trend == "No current data"
        for card in cards
    )