"""
Tests for the Development page.
"""

from datetime import date, datetime

from app.components.development_page import (
    _daily_load_chart_rows,
    _daily_training_load_chart,
    _development_chart_rows,
    _development_intensity_html,
    _development_interpretation_html,
    _development_load_form_chart,
    _development_performance_references_html,
    _development_recovery_context,
    _pace_label,
    _development_overall_status,
    _development_sport_volume_html,
    _sport_volume_duration_label,
    _development_summary_cards_html,
    _form_status,
    _load_status,
    _recovery_status,
    show_development_page,
)

from performancelab.presentation import (
    DevelopmentData,
    DevelopmentHeartRateZoneData,
    DevelopmentIntensityData,
    DevelopmentPaceZoneData,
    DevelopmentPerformanceReferencesData,
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
        recovery_balance=-8.0,
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
        "Balance -8.0"
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

def test_builds_development_load_form_chart():

    chart = (
        _development_load_form_chart(
            create_development_data()
        )
    )

    specification = (
        chart.to_dict()
    )

    assert (
        len(
            specification["layer"]
        )
        == 3
    )

    assert (
        specification["resolve"]
        ["scale"]
        ["y"]
        == "independent"
    )

    assert (
        specification["height"]
        == 225
    )

def test_builds_development_interpretation():

    result = (
        _development_interpretation_html(
            create_development_data()
        )
    )

    assert (
        "development-interpretation-card"
        in result
    )

    assert (
        "Interpretation"
        in result
    )

    assert (
        "Training load"
        in result
    )

    assert (
        "Recovery"
        in result
    )

    assert (
        "Form"
        in result
    )

    assert (
        "Recommendation"
        in result
    )

    assert (
        "150 AU"
        in result
    )

    assert (
        "120 AU"
        in result
    )

    assert (
        "-7.2 TSB"
        in result
    )


def test_prioritises_low_recovery_in_overall_status():

    development = (
        create_development_data()
    )

    result = (
        _development_overall_status(
            development
        )
    )

    assert result == (
        "Recovery deserves attention",
        (
            "The current state suggests that "
            "recovery should take priority."
        ),
    )

def test_builds_daily_training_load_chart():

    chart = (
        _daily_training_load_chart(
            create_development_data()
        )
    )

    specification = (
        chart.to_dict()
    )

    assert (
        len(
            specification["layer"]
        )
        == 2
    )

    assert (
        specification["height"]
        == 175
    )

    assert (
        specification["layer"][0]
        ["mark"]["type"]
        == "bar"
    )

    assert (
        specification["layer"][1]
        ["mark"]["type"]
        == "line"
    )

def test_formats_sport_volume_duration():

    assert (
        _sport_volume_duration_label(
            5400.0
        )
        == "1h 30m"
    )

    assert (
        _sport_volume_duration_label(
            7200.0
        )
        == "2h"
    )


def test_builds_sport_volume_card():

    development = (
        create_development_data()
    )

    development = type(
        "DevelopmentWithVolume",
        (),
        {
            **development.__dict__,
            "sport_volume": (
                type(
                    "SportVolume",
                    (),
                    {
                        "sport": (
                            "Trail Running"
                        ),
                        "duration_seconds": (
                            9000.0
                        ),
                        "distance": 20.0,
                        "sessions": 2,
                    },
                )(),
                type(
                    "SportVolume",
                    (),
                    {
                        "sport": "Cycling",
                        "duration_seconds": (
                            7200.0
                        ),
                        "distance": 40.0,
                        "sessions": 1,
                    },
                )(),
            ),
        },
    )()

    result = (
        _development_sport_volume_html(
            development
        )
    )

    assert (
        "Volume by sport"
        in result
    )

    assert (
        "Trail Running"
        in result
    )

    assert (
        "Cycling"
        in result
    )

    assert (
        "2h 30m"
        in result
    )

    assert (
        "60 km"
        in result
    )

    assert (
        "3 sessions"
        in result
    )

def test_builds_development_intensity_card():

    development = (
        create_development_data()
    )

    development = type(
        "DevelopmentWithIntensity",
        (),
        {
            **development.__dict__,
            "intensity": (
                DevelopmentIntensityData(
                    zones=(
                        DevelopmentHeartRateZoneData(
                            name="Z1",
                            lower_bpm=120,
                            upper_bpm=135,
                            duration_seconds=1200.0,
                            percentage=20.0,
                        ),
                        DevelopmentHeartRateZoneData(
                            name="Z2",
                            lower_bpm=136,
                            upper_bpm=150,
                            duration_seconds=2400.0,
                            percentage=40.0,
                        ),
                    ),
                    zone_source="manual",
                    heart_rate_seconds=3600.0,
                    average_rpe=6.2,
                    sessions_with_rpe=10,
                    high_rpe_sessions=2,
                )
            ),
        },
    )()

    result = (
        _development_intensity_html(
            development
        )
    )

    assert "Intensity & RPE" in result
    assert "Manual HR zones" in result
    assert "Z1" in result
    assert "Z2" in result
    assert "20%" in result
    assert "40%" in result
    assert "Average RPE" in result
    assert "6.2" in result
    assert "RPE &gt; 8" in result

def test_formats_pace_label():

    assert (
        _pace_label(
            5.2
        )
        == "5:12 /km"
    )

    assert (
        _pace_label(
            None
        )
        == "—"
    )


def test_builds_performance_references_card():

    development = (
        create_development_data()
    )

    development = type(
        "DevelopmentWithReferences",
        (),
        {
            **development.__dict__,
            "performance_references": (
                DevelopmentPerformanceReferencesData(
                    pace_zones=(
                        DevelopmentPaceZoneData(
                            name="Z1",
                            faster_pace=6.0,
                            slower_pace=6.5,
                        ),
                        DevelopmentPaceZoneData(
                            name="Z2",
                            faster_pace=5.5,
                            slower_pace=6.0,
                        ),
                    ),
                    easy_pace=6.1,
                    tempo_pace=5.1,
                    lt2_pace=4.95,
                    threshold_hr=177,
                    ftp=220,
                )
            ),
        },
    )()

    result = (
        _development_performance_references_html(
            development
        )
    )

    assert (
        "Pace & thresholds"
        in result
    )

    assert "Z1" in result
    assert "Z2" in result
    assert "6:00 /km" in result
    assert "6:30 /km" in result
    assert "Easy pace" in result
    assert "Tempo" in result
    assert "LT2 pace" in result
    assert "177 bpm" in result
    assert "220 W" in result

def test_formats_time_aware_recovery_context():

    development = (
        create_development_data()
    )

    development = type(
        "TimeAwareDevelopment",
        (),
        {
            **development.__dict__,
            "recovery_is_time_aware": True,
            "hours_since_last_workout": (
                30.4
            ),
            "recovery_reference_time": (
                datetime(
                    2026,
                    8,
                    12,
                    14,
                    5,
                )
            ),
        },
    )()

    assert (
        _development_recovery_context(
            development
        )
        == (
            "Balance -8.0"
            " · 30 h since last session"
            " · Updated 14:05"
        )
    )


def test_formats_daily_development_fallback():

    development = (
        create_development_data()
    )

    assert (
        _development_recovery_context(
            development
        )
        == (
            "Balance -8.0"
            " · Daily estimate"
        )
    )