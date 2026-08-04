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

    today = date.today()

    athlete.history.add(

        create_workout(

            today - timedelta(days=4),

            timedelta(hours=1),

            5,

        )

    )

    athlete.history.add(

        create_workout(

            today - timedelta(days=2),

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

        today - timedelta(days=4),

        today - timedelta(days=3),

        today - timedelta(days=2),

        today - timedelta(days=1),

        today,

    ]

    assert data["performance"].load == [

        300,

        0.0,

        360,

        0.0,

        0.0,

    ]

    assert len(

        data["performance"].ctl

    ) == 5

    assert len(

        data["performance"].atl

    ) == 5

    assert len(

        data["performance"].tsb

    ) == 5

# ======================================================

def test_performance_series_have_same_length():

    athlete = Athlete(name="Pedro")

    athlete.history.add(

        create_workout(

            date.today() - timedelta(days=4),

            timedelta(hours=1),

            5,

        )

    )

    athlete.history.add(

        create_workout(

            date.today(),

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

def test_next_workout_skips_completed_planned_day():

    athlete = Athlete(
        name="Pedro"
    )

    today = date.today()
    future_day = today + timedelta(
        days=2
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            today,
            time.min,
        ),
        sport="Trail Running",
        title="Long Run",
        duration=timedelta(
            minutes=90,
        ),
    )

    athlete.training_plan.schedule(
        scheduled_at=datetime.combine(
            future_day,
            time.min,
        ),
        sport="Road Running",
        title="LT2 Run",
        duration=timedelta(
            minutes=60,
        ),
    )

    athlete.history.add(
        create_workout(
            today,
            timedelta(
                minutes=152,
            ),
            7.5,
        )
    )

    planning = DashboardData(
        athlete
    ).planning

    assert (
        planning.next_workout.title
        == "LT2 Run"
    )

    assert (
        planning.next_workout.scheduled_at.date()
        == future_day
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

def test_latest_activity_uses_sensor_metrics():

    athlete = Athlete(
        name="Pedro"
    )

    workout = create_workout(
        date(2026, 7, 30),
        timedelta(minutes=73),
        7,
    )

    workout.feedback.estimated_rpe = 6.8

    workout.sensors.add(
        "heart_rate",
        [
            {"value": 150},
            {"value": 170},
            {"value": 190},
        ],
    )

    workout.sensors.add(
        "power",
        [
            {"value": 200},
            {"value": 220},
        ],
    )

    workout.sensors.add(
        "cadence",
        [
            {"value": 168},
            {"value": 172},
        ],
    )

    workout.sensors.add(
        "active_calories",
        [
            {"value": 850},
        ],
    )

    athlete.history.add(
        workout
    )

    latest = DashboardData(
        athlete
    ).latest_activity

    assert latest.average_heart_rate == 170
    assert latest.maximum_heart_rate == 190
    assert latest.average_power == 210
    assert latest.maximum_power == 220
    assert latest.average_cadence == 170
    assert latest.maximum_cadence == 172
    assert latest.is_cycling is False
    assert latest.average_speed is None
    assert latest.active_calories == 850
    assert latest.rpe == 7

def test_cycling_activity_exposes_average_speed():

    athlete = Athlete(
        name="Pedro"
    )

    workout = Workout()

    workout.info.sport = "Cycling"
    workout.info.date = date(
        2026,
        8,
        2,
    )
    workout.info.duration = timedelta(
        hours=2,
        minutes=30,
    )
    workout.info.distance = 50.0

    workout.sensors.add(
        "power",
        [
            {"value": 150},
            {"value": 300},
        ],
    )

    workout.sensors.add(
        "cadence",
        [
            {"value": 60},
            {"value": 95},
        ],
    )

    athlete.history.add(
        workout
    )

    latest = DashboardData(
        athlete
    ).latest_activity

    assert latest.is_cycling is True
    assert latest.average_speed == 20.0
    assert latest.average_power == 225
    assert latest.maximum_power == 300
    assert latest.average_cadence == 77.5
    assert latest.maximum_cadence == 95