"""
Tests for the Development page.
"""

from datetime import date

from app.components.development_page import (
    _daily_load_chart_rows,
    _development_chart_rows,
    show_development_page,
)
from performancelab.presentation import (
    DevelopmentData,
)


def create_development_data():
    return DevelopmentData(
        dates=(
            date(2026, 8, 1),
            date(2026, 8, 2),
        ),
        daily_load=(
            300.0,
            0.0,
        ),
        fitness=(
            10.0,
            9.8,
        ),
        fatigue=(
            20.0,
            17.0,
        ),
        form=(
            -10.0,
            -7.2,
        ),
        current_fitness=9.8,
        current_fatigue=17.0,
        current_form=-7.2,
        recovery_score=42.0,
        recovery_status="Recovery needed",
        recovery_recommendation=(
            "Prioritise recovery."
        ),
        acute_load=150.0,
        chronic_load=120.0,
        ramp_rate=25.0,
        load_status="High load",
        load_recommendation=(
            "Reduce demanding training."
        ),
    )


def test_show_development_page_exists():

    assert callable(
        show_development_page
    )


def test_builds_performance_chart_rows():

    rows = _development_chart_rows(
        create_development_data()
    )

    assert rows == [
        {
            "Date": date(
                2026,
                8,
                1,
            ),
            "Fitness": 10.0,
            "Fatigue": 20.0,
            "Form": -10.0,
        },
        {
            "Date": date(
                2026,
                8,
                2,
            ),
            "Fitness": 9.8,
            "Fatigue": 17.0,
            "Form": -7.2,
        },
    ]


def test_builds_daily_load_chart_rows():

    rows = _daily_load_chart_rows(
        create_development_data()
    )

    assert rows == [
        {
            "Date": date(
                2026,
                8,
                1,
            ),
            "Training load": 300.0,
        },
        {
            "Date": date(
                2026,
                8,
                2,
            ),
            "Training load": 0.0,
        },
    ]