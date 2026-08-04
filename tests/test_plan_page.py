"""
Tests for the complete training-plan page.
"""

from datetime import date, datetime, timedelta
from types import SimpleNamespace

from app.components.plan_page import (
    _current_plan_week,
    _plan_summary_metrics,
    _progression_chart_data,
    _week_duration_label,
    _status_label,
    _week_html,
    _week_is_current,
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

    first_week = create_week()

    second_workout = PlanWorkoutData(
        scheduled_at=datetime(
            2026,
            8,
            11,
            8,
            0,
        ),
        sport="Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=45,
        ),
        distance=8,
        elevation_gain=50,
        intensity="Hard",
        phase="Peak",
        planned_load=315.0,
        is_race=False,
        status="pending",
        prescription_summary=None,
        structure=(),
    )

    second_week = PlanWeekData(
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
        workouts=(
            second_workout,
        ),
    )

    result = _progression_chart_data(
        (
            first_week,
            second_week,
        )
    )

    assert result == [
        {
            "Date": (
                "2026-08-04T08:00:00"
            ),
            "Planned load": 180.0,
            "Session": "Easy Run",
            "Session type": "Training",
        },
        {
            "Date": (
                "2026-08-11T08:00:00"
            ),
            "Planned load": 315.0,
            "Session": "LT2 Run",
            "Session type": "Training",
        },
    ]


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