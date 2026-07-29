"""
PerformanceLab

Tests for Dashboard Data.
"""

from datetime import date, datetime, time, timedelta

import streamlit as st

from performancelab import Athlete, Workout
from performancelab.presentation import DashboardData

from performancelab.presentation.dashboard_models import (
    WeeklyPlanDayData,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(
    workout_date,
    duration,
    rpe,
):

    workout = Workout()

    workout.info.sport = "Running"
    workout.info.date = workout_date
    workout.info.duration = duration

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def test_empty_dashboard():

    athlete = Athlete(name="Pedro")

    dashboard = DashboardData(athlete)

    data = dashboard.build()

    assert data["athlete"].name == "Pedro"

    assert data["athlete"].sports == []

    assert data["summary"].workouts == 0

    assert data["summary"].sports == 0

    assert data["summary"].training_days == 0

    assert data["summary"].total_duration == timedelta(0)

    assert data["summary"].average_rpe is None

    assert data["summary"].ctl == 0.0

    assert data["summary"].atl == 0.0

    assert data["summary"].tsb == 0.0

    assert data["performance"].dates == []

    assert data["performance"].load == []

    assert data["performance"].ctl == []

    assert data["performance"].atl == []

    assert data["performance"].tsb == []

# ======================================================

def test_recovery_uses_training_state():

    athlete = Athlete(name="Pedro")

    training_state = athlete.analytics.training_state

    recovery = DashboardData(athlete).recovery

    assert recovery.score == training_state.recovery_score

    assert recovery.status == training_state.recovery_status

    assert (
        recovery.recommendation
        == training_state.recovery_recommendation
    )

    assert recovery.trend == training_state.training_trend


# ======================================================

def test_dashboard_with_training():

    athlete = Athlete(name="Pedro")

    athlete.history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(hours=1),

            5,

        )

    )

    athlete.history.add(

        create_workout(

            date(2026, 7, 3),

            timedelta(hours=1),

            6,

        )

    )

    dashboard = DashboardData(athlete)

    data = dashboard.build()

    assert data["athlete"].name == "Pedro"

    assert data["athlete"].sports == [

        "Running",

    ]

    assert data["summary"].workouts == 2

    assert data["summary"].sports == 1

    assert data["summary"].training_days == 2

    assert data["summary"].total_duration == timedelta(
        hours=2
    )

    assert data["summary"].average_rpe == 5.5

    assert data["performance"].dates == [

        date(2026, 7, 1),

        date(2026, 7, 2),

        date(2026, 7, 3),

    ]

    assert data["performance"].load == [

        300,

        0.0,

        360,

    ]

    assert len(

        data["performance"].ctl

    ) == 3

    assert len(

        data["performance"].atl

    ) == 3

    assert len(

        data["performance"].tsb

    ) == 3


# ======================================================

def test_performance_series_have_same_length():

    athlete = Athlete(name="Pedro")

    athlete.history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(hours=1),

            5,

        )

    )

    athlete.history.add(

        create_workout(

            date(2026, 7, 5),

            timedelta(hours=2),

            7,

        )

    )

    performance = DashboardData(

        athlete

    ).performance

    lengths = {

        len(performance.dates),

        len(performance.load),

        len(performance.ctl),

        len(performance.atl),

        len(performance.tsb),

    }

    assert lengths == {5}

def test_next_workout_remains_anchored_to_today():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            today,
            time.min,
        ),
        sport="Running",
        title="Current Workout",
        duration=timedelta(
            minutes=45
        ),
    )

    future_day = today + timedelta(
        days=14
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            future_day,
            time.min,
        ),
        sport="Running",
        title="Future Workout",
        duration=timedelta(
            minutes=45
        ),
    )

    st.session_state[
        "planning_window_center_date"
    ] = future_day

    try:

        planning = DashboardData(
            athlete
        ).planning

    finally:

        st.session_state.pop(
            "planning_window_center_date",
            None,
        )

    assert (
        planning.weekly_plan.start_date
        == future_day - timedelta(days=3)
    )

    assert (
        planning.next_workout.title
        == "Current Workout"
    )
def test_weekly_plan_day_carries_workout_structure():

    day = WeeklyPlanDayData(
        day=date(2026, 7, 29),
        status="planned",
        sport="Trail Running",
        title="Hill Run",
        duration=timedelta(hours=1),
        distance=None,
        intensity="Hard",
        structure=(
            "Warm up 15 min",
            "5×5 min uphill",
            (
                "Recover 2 min easy downhill "
                "between repetitions"
            ),
            "Cool down 10 min",
        ),
    )

    assert day.structure == (
        "Warm up 15 min",
        "5×5 min uphill",
        (
            "Recover 2 min easy downhill "
            "between repetitions"
        ),
        "Cool down 10 min",
    )