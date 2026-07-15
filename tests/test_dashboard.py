"""
PerformanceLab

Tests for Dashboard Data.
"""

from datetime import date, timedelta

from performancelab import Athlete, Workout
from performancelab.presentation import DashboardData


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

    assert data["athlete"]["name"] == "Pedro"

    assert data["athlete"]["sports"] == []

    assert data["summary"]["workouts"] == 0

    assert data["summary"]["training_days"] == 0

    assert data["summary"]["ctl"] == 0.0

    assert data["summary"]["atl"] == 0.0

    assert data["summary"]["tsb"] == 0.0

    assert data["performance"]["dates"] == []

    assert data["performance"]["load"] == []

    assert data["performance"]["ctl"] == []

    assert data["performance"]["atl"] == []

    assert data["performance"]["tsb"] == []


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

    assert data["athlete"]["name"] == "Pedro"

    assert data["athlete"]["sports"] == [

        "Running",

    ]

    assert data["summary"]["workouts"] == 2

    assert data["summary"]["training_days"] == 2

    assert data["performance"]["dates"] == [

        date(2026, 7, 1),

        date(2026, 7, 2),

        date(2026, 7, 3),

    ]

    assert data["performance"]["load"] == [

        300,

        0.0,

        360,

    ]

    assert len(

        data["performance"]["ctl"]

    ) == 3

    assert len(

        data["performance"]["atl"]

    ) == 3

    assert len(

        data["performance"]["tsb"]

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

        len(performance["dates"]),

        len(performance["load"]),

        len(performance["ctl"]),

        len(performance["atl"]),

        len(performance["tsb"]),

    }

    assert lengths == {5}