"""
Tests for the Development page.
"""

from datetime import date

from app.components.development_page import (
    _daily_load_chart_rows,
    _development_chart_rows,
    _development_summary_cards_html,
    _form_status,
    _load_status,
    _recovery_status,
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

def test_interprets_form_status():

    assert (
        _form_status(
            8.0
        )
        == "Fresh"
    )

    assert (
        _form_status(
            2.0
        )
        == "Balanced"
    )

    assert (
        _form_status(
            -10.0
        )
        == "Loaded"
    )

    assert (
        _form_status(
            -20.0
        )
        == "Fatigued"
    )


def test_interprets_recovery_status():

    assert (
        _recovery_status(
            80.0
        )
        == "Good"
    )

    assert (
        _recovery_status(
            60.0
        )
        == "Moderate"
    )

    assert (
        _recovery_status(
            40.0
        )
        == "Low"
    )


def test_interprets_load_status():

    assert (
        _load_status(
            120.0,
            100.0,
        )
        == "Stable"
    )

    assert (
        _load_status(
            130.0,
            100.0,
        )
        == "Elevated"
    )

    assert (
        _load_status(
            70.0,
            100.0,
        )
        == "Reduced"
    )


def test_builds_development_summary_cards():

    result = (
        _development_summary_cards_html(
            create_development_data()
        )
    )

    assert (
        "development-kpi-grid"
        in result
    )

    assert (
        "Recovery"
        in result
    )

    assert (
        "Chronic load"
        in result
    )

    assert (
        "Form"
        in result
    )

    assert (
        "Acute load"
        in result
    )

    assert (
        "42"
        in result
    )

    assert (
        "120"
        in result
    )

    assert (
        "-7.2"
        in result
    )

    assert (
        "150"
        in result
    )