"""
Tests for the complete training-plan page.
"""

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from app.components.plan_page import (
    _current_plan_week,
    _plan_chart_data,
    _plan_volume_chart_data,
    _plan_summary_metrics,
    _weekly_planned_load_average_data,
    _planned_load_chart_series,
    _sidebar_phase_html,
    _sidebar_session_marker_class,
    _sidebar_week_html,
    _week_duration_label,
    _status_label,
    _week_html,
    _week_is_current,
    _week_summary_label,
     show_plan_page,
)
from performancelab.presentation import (
    PlanWeekData,
    PlanWorkoutData,
)


def create_week(
    *,
    status: str = "pending",
) -> PlanWeekData:

    workout = PlanWorkoutData(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            minutes=60,
        ),
        distance=10,
        elevation_gain=100,
        intensity="Easy",
        phase="Build",
        planned_load=180.0,
        is_race=False,
        status=status,
        prescription_summary=(
            "60 min easy"
        ),
        structure=(),
    )

    return PlanWeekData(
        start_date=date(
            2026,
            8,
            3,
        ),
        end_date=date(
            2026,
            8,
            9,
        ),
        phase="Build",
        planned_load=180,
        workouts=(
            workout,
        ),
    )

def test_finds_current_plan_week():

    current = create_week()

    future = PlanWeekData(
        start_date=date(
            2026,
            8,
            10,
        ),
        end_date=date(
            2026,
            8,
            16,
        ),
        phase="Peak",
        planned_load=315.0,
        workouts=(),
    )

    result = _current_plan_week(
        (
            current,
            future,
        ),
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert result is current


def test_returns_none_outside_plan_weeks():

    result = _current_plan_week(
        (
            create_week(),
        ),
        reference_day=date(
            2026,
            8,
            20,
        ),
    )

    assert result is None

def test_formats_current_week_duration():

    first = PlanWorkoutData(
        scheduled_at=datetime(
            2026,
            8,
            4,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            hours=1,
            minutes=8,
        ),
        distance=10,
        elevation_gain=100,
        intensity="Hard",
        phase="Peak",
        planned_load=476.0,
        is_race=False,
        status="pending",
        prescription_summary=None,
        structure=(),
    )

    second = PlanWorkoutData(
        scheduled_at=datetime(
            2026,
            8,
            6,
            8,
            0,
        ),
        sport="Running",
        title="Easy Run",
        duration=timedelta(
            hours=2,
        ),
        distance=20,
        elevation_gain=300,
        intensity="Easy",
        phase="Peak",
        planned_load=360.0,
        is_race=False,
        status="pending",
        prescription_summary=None,
        structure=(),
    )

    week = PlanWeekData(
        start_date=date(
            2026,
            8,
            3,
        ),
        end_date=date(
            2026,
            8,
            9,
        ),
        phase="Peak",
        planned_load=836.0,
        workouts=(
            first,
            second,
        ),
    )

    assert (
        _week_duration_label(
            week
        )
        == "3h08"
    )



def test_builds_plan_summary_metrics():

    plan = SimpleNamespace(
        weeks=(
            SimpleNamespace(
                planned_load=876.0
            ),
            SimpleNamespace(
                planned_load=1035.0
            ),
        ),
        progression=(
            SimpleNamespace(
                distance=38.0,
                elevation_gain=950.0,
            ),
            SimpleNamespace(
                distance=42.0,
                elevation_gain=1100.0,
            ),
        ),
    )

    result = _plan_summary_metrics(
        plan
    )

    assert result == {
        "Horizon": "2 weeks",
        "Planned load": "1911 AU",
        "Max distance": "42 km/week",
        "Max elevation": "1100 m/week",
    }



def test_builds_planned_session_chart_data():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                8,
                4,
            ),
            title="Easy Run",
            phase="Build",
            planned_load=180.0,
            distance=10.0,
            is_race=False,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                11,
            ),
            title="LT2 Run",
            phase="Peak",
            planned_load=315.0,
            distance=8.0,
            is_race=False,
        ),
        SimpleNamespace(
            day=date(
                2026,
                9,
                13,
            ),
            title="Race",
            phase="Race",
            planned_load=900.0,
            distance=25.0,
            is_race=True,
        ),
    )

    result = _plan_chart_data(
        chart_points
    )

    assert result == [
        {
            "Date": "2026-08-04",
            "Planned load": 180.0,
            "Session": "Easy Run",
            "Phase": "Build",
            "Session type": "Training",
        },
        {
            "Date": "2026-08-11",
            "Planned load": 315.0,
            "Session": "LT2 Run",
            "Phase": "Peak",
            "Session type": "Training",
        },
        {
            "Date": "2026-09-13",
            "Planned load": 900.0,
            "Session": "Race",
            "Phase": "Race",
            "Session type": "Race",
        },
    ]


def test_omits_chart_points_without_planned_load():

    chart_point = SimpleNamespace(
        day=date(
            2026,
            8,
            4,
        ),
        title="Unloaded session",
        phase="Build",
        planned_load=None,
        distance=10.0,
        is_race=False,
    )

    assert (
        _plan_chart_data(
            (
                chart_point,
            )
        )
        == []
    )

def test_show_plan_page_exists():

    assert callable(
        show_plan_page
    )


def test_identifies_current_week():

    week = create_week()

    assert _week_is_current(
        week,
        reference_day=date(
            2026,
            8,
            5,
        ),
    )

    assert not _week_is_current(
        week,
        reference_day=date(
            2026,
            8,
            10,
        ),
    )


def test_formats_plan_status():

    assert _status_label(
        "equivalent"
    ) == "Equivalent"

    assert _status_label(
        "outside_plan"
    ) == "Outside Plan"


def test_week_html_contains_workout():

    html = _week_html(
        create_week(
            status="modified"
        )
    )

    assert "Easy Run" in html
    assert "60 min easy" in html
    assert "1h 00m" in html
    assert "status-modified" in html
    assert "Modified" in html


def test_week_html_escapes_workout_title():

    week = create_week()

    unsafe_workout = PlanWorkoutData(
        scheduled_at=(
            week.workouts[0]
            .scheduled_at
        ),
        sport="Running",
        title="<script>Run</script>",
        duration=timedelta(
            minutes=60,
        ),
        distance=10,
        elevation_gain=100,
        intensity="Easy",
        phase="Build",
        planned_load=180.0,
        is_race=False,
        status="pending",
        prescription_summary=None,
        structure=(),
    )

    unsafe_week = PlanWeekData(
        start_date=week.start_date,
        end_date=week.end_date,
        phase=week.phase,
        planned_load=week.planned_load,
        workouts=(
            unsafe_workout,
        ),
    )

    html = _week_html(
        unsafe_week
    )

    assert "<script>" not in html
    assert "&lt;script&gt;" in html

def test_aggregates_weekly_training_volume_and_races():

    training_one = SimpleNamespace(
        scheduled_at=datetime(
            2026,
            9,
            8,
            8,
            0,
        ),
        distance=10.0,
        elevation_gain=300.0,
        is_race=False,
    )

    training_two = SimpleNamespace(
        scheduled_at=datetime(
            2026,
            9,
            10,
            8,
            0,
        ),
        distance=8.0,
        elevation_gain=200.0,
        is_race=False,
    )

    race = SimpleNamespace(
        scheduled_at=datetime(
            2026,
            9,
            13,
            8,
            0,
        ),
        distance=42.0,
        elevation_gain=1800.0,
        is_race=True,
    )

    plan = SimpleNamespace(
        start_date=date(
            2026,
            9,
            7,
        ),
        end_date=date(
            2026,
            9,
            20,
        ),
        weeks=(
            SimpleNamespace(
                start_date=date(
                    2026,
                    9,
                    7,
                ),
                end_date=date(
                    2026,
                    9,
                    13,
                ),
                workouts=(
                    training_one,
                    training_two,
                    race,
                ),
            ),
            SimpleNamespace(
                start_date=date(
                    2026,
                    9,
                    14,
                ),
                end_date=date(
                    2026,
                    9,
                    20,
                ),
                workouts=(),
            ),
        ),
    )

    result = (
        _plan_volume_chart_data(
            plan
        )
    )

    assert result == [
        {
            "Date": "2026-09-07",
            "Distance": 18.0,
            "Elevation": 500.0,
            "Point type": "Weekly training",
        },
        {
            "Date": "2026-09-13",
            "Distance": 42.0,
            "Elevation": 1800.0,
            "Point type": "Race",
        },
        {
            "Date": "2026-09-20",
            "Distance": 0.0,
            "Elevation": 0.0,
            "Point type": "Weekly training",
        },
    ]
    
def test_keeps_recovery_until_exact_plan_end():

    plan = SimpleNamespace(
        start_date=date(
            2026,
            8,
            2,
        ),
        end_date=date(
            2026,
            10,
            4,
        ),
        weeks=(
            SimpleNamespace(
                start_date=date(
                    2026,
                    9,
                    28,
                ),
                end_date=date(
                    2026,
                    10,
                    4,
                ),
                workouts=(),
            ),
        ),
    )

    assert (
        _plan_volume_chart_data(
            plan
        )
        == [
            {
                "Date": "2026-10-04",
                "Distance": 0.0,
                "Elevation": 0.0,
                "Point type": "Weekly training",
            },
        ]
    )

def test_builds_current_phase_sidebar_card():

    phase = SimpleNamespace(
        name="Peak",
        objective=(
            "Increase race-specific endurance "
            "and key-session quality."
        ),
        start_date=date(
            2026,
            8,
            17,
        ),
        end_date=date(
            2026,
            9,
            6,
        ),
        weeks_remaining=2,
    )

    result = (
        _sidebar_phase_html(
            phase
        )
    )

    assert "Current phase" in result
    assert "Peak" in result

    assert (
        "Increase race-specific endurance"
        in result
    )

    assert "17 Aug – 06 Sep" in result
    assert "2" in result
    assert "weeks remaining" in result


def test_builds_empty_phase_sidebar_card():

    result = (
        _sidebar_phase_html(
            None
        )
    )

    assert "Current phase" in result
    assert "No current phase." in result


def test_builds_current_week_sidebar_card():

    week = create_week()

    result = (
        _sidebar_week_html(
            week
        )
    )

    assert "Current week" in result
    assert "03 Aug – 09 Aug" in result
    assert "Build" in result
    assert "1 session" in result
    assert "1h" in result
    assert "180 AU" in result
    assert "TUE 04" in result
    assert "Easy Run" in result


def test_builds_empty_week_sidebar_card():

    result = (
        _sidebar_week_html(
            None
        )
    )

    assert "Current week" in result

    assert (
        "No current plan week."
        in result
    )


def test_marks_quality_session_in_sidebar():

    workout = SimpleNamespace(
        is_race=False,
        intensity="Hard",
        title="LT2 Run",
    )

    assert (
        _sidebar_session_marker_class(
            workout
        )
        == "quality"
    )


def test_marks_race_session_in_sidebar():

    workout = SimpleNamespace(
        is_race=True,
        intensity="Race effort",
        title="Race",
    )

    assert (
        _sidebar_session_marker_class(
            workout
        )
        == "race"
    )


def test_marks_easy_session_as_aerobic():

    workout = SimpleNamespace(
        is_race=False,
        intensity="Easy",
        title="Easy Run",
    )

    assert (
        _sidebar_session_marker_class(
            workout
        )
        == "aerobic"
    )

def test_separates_training_load_from_race_markers():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                8,
                4,
            ),
            title="Easy Run",
            phase="Build",
            planned_load=180.0,
            is_race=False,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                11,
            ),
            title="LT2 Run",
            phase="Peak",
            planned_load=400.0,
            is_race=False,
        ),
        SimpleNamespace(
            day=date(
                2026,
                9,
                27,
            ),
            title="Trail Race",
            phase="Race",
            planned_load=2200.0,
            is_race=True,
        ),
    )

    (
        training_rows,
        race_rows,
    ) = _planned_load_chart_series(
        chart_points
    )

    assert [
        row["Session"]
        for row in training_rows
    ] == [
        "Easy Run",
        "LT2 Run",
    ]

    assert len(
        race_rows
    ) == 1

    assert (
        race_rows[0]["Session"]
        == "Trail Race"
    )

    assert (
        race_rows[0]["Planned load"]
        == 2200.0
    )

    assert (
        race_rows[0]["Marker load"]
        == 432.0
    )


def test_positions_race_marker_without_training_sessions():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                9,
                27,
            ),
            title="Trail Race",
            phase="Race",
            planned_load=2200.0,
            is_race=True,
        ),
    )

    (
        training_rows,
        race_rows,
    ) = _planned_load_chart_series(
        chart_points
    )

    assert training_rows == []

    assert (
        race_rows[0]["Marker load"]
        == 2200.0
    )

def test_builds_current_week_summary_label():

    week = create_week()

    result = (
        _week_summary_label(
            week,
            reference_day=date(
                2026,
                8,
                5,
            ),
        )
    )

    assert result == (
        "● 03 Aug – 09 Aug"
        "  ·  Build"
        "  ·  1 session"
        "  ·  1h"
        "  ·  180 AU"
    )


def test_builds_future_week_summary_without_marker():

    week = create_week()

    result = (
        _week_summary_label(
            week,
            reference_day=date(
                2026,
                7,
                20,
            ),
        )
    )

    assert result == (
        "03 Aug – 09 Aug"
        "  ·  Build"
        "  ·  1 session"
        "  ·  1h"
        "  ·  180 AU"
    )


def test_builds_plural_week_summary():

    first = SimpleNamespace(
        duration=timedelta(
            minutes=45,
        ),
    )

    second = SimpleNamespace(
        duration=timedelta(
            minutes=75,
        ),
    )

    week = SimpleNamespace(
        start_date=date(
            2026,
            8,
            10,
        ),
        end_date=date(
            2026,
            8,
            16,
        ),
        phase="Peak",
        planned_load=720.0,
        workouts=(
            first,
            second,
        ),
    )

    result = (
        _week_summary_label(
            week,
            reference_day=date(
                2026,
                8,
                5,
            ),
        )
    )

    assert result == (
        "10 Aug – 16 Aug"
        "  ·  Peak"
        "  ·  2 sessions"
        "  ·  2h"
        "  ·  720 AU"
    )

def test_calculates_weekly_planned_load_averages():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                8,
                3,
            ),
            planned_load=100.0,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                5,
            ),
            planned_load=200.0,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                10,
            ),
            planned_load=300.0,
        ),
    )

    result = (
        _weekly_planned_load_average_data(
            chart_points
        )
    )

    assert result == [
        {
            "Date": "2026-08-03",
            "Weekly average load": 150.0,
            "Session count": 2,
        },
        {
            "Date": "2026-08-10",
            "Weekly average load": 300.0,
            "Session count": 1,
        },
    ]


def test_weekly_average_includes_race_load():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                9,
                21,
            ),
            planned_load=100.0,
        ),
        SimpleNamespace(
            day=date(
                2026,
                9,
                23,
            ),
            planned_load=200.0,
        ),
        SimpleNamespace(
            day=date(
                2026,
                9,
                27,
            ),
            planned_load=2200.0,
        ),
    )

    result = (
        _weekly_planned_load_average_data(
            chart_points
        )
    )

    assert result == [
        {
            "Date": "2026-09-21",
            "Weekly average load": (
                2500.0 / 3
            ),
            "Session count": 3,
        },
    ]


def test_weekly_average_ignores_missing_load():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                8,
                3,
            ),
            planned_load=100.0,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                5,
            ),
            planned_load=None,
        ),
        SimpleNamespace(
            day=date(
                2026,
                8,
                7,
            ),
            planned_load=300.0,
        ),
    )

    result = (
        _weekly_planned_load_average_data(
            chart_points
        )
    )

    assert result == [
        {
            "Date": "2026-08-03",
            "Weekly average load": 200.0,
            "Session count": 2,
        },
    ]


def test_returns_empty_weekly_average_without_load():

    chart_points = (
        SimpleNamespace(
            day=date(
                2026,
                8,
                3,
            ),
            planned_load=None,
        ),
    )

    result = (
        _weekly_planned_load_average_data(
            chart_points
        )
    )

    assert result == []