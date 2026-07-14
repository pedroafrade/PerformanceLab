"""
PerformanceLab

Tests for Training Load.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import (
    WeeklySummary,
    MonthlySummary,
)
from performancelab.training.load import (
    workout_load,
    weekly_load,
    monthly_load,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(duration, rpe):

    workout = Workout()

    workout.info.date = date.today()
    workout.info.duration = duration

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def create_week():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),

        end_date=date(2026, 7, 12),

    )

    return week


# ======================================================
# Workout
# ======================================================

def test_workout_load():

    workout = create_workout(

        timedelta(hours=1),

        5,

    )

    assert workout_load(workout) == 300


# ======================================================

def test_workout_without_duration():

    workout = create_workout(

        None,

        5,

    )

    assert workout_load(workout) is None


# ======================================================

def test_workout_without_rpe():

    workout = create_workout(

        timedelta(hours=1),

        None,

    )

    assert workout_load(workout) is None


# ======================================================
# Weekly
# ======================================================

def test_weekly_load():

    week = create_week()

    week.history.add(

        create_workout(

            timedelta(hours=1),

            5,

        )

    )

    week.history.add(

        create_workout(

            timedelta(minutes=30),

            8,

        )

    )

    assert weekly_load(week) == 540


# ======================================================

def test_empty_week():

    week = create_week()

    assert weekly_load(week) == 0


# ======================================================
# Monthly
# ======================================================

def test_monthly_load():

    week1 = create_week()

    week1.history.add(

        create_workout(

            timedelta(hours=1),

            5,

        )

    )

    week2 = WeeklySummary(

        start_date=date(2026, 7, 13),

        end_date=date(2026, 7, 19),

    )

    week2.history.add(

        create_workout(

            timedelta(hours=2),

            4,

        )

    )

    month = MonthlySummary(

        year=2026,

        month=7,

    )

    month.add_week(week1)

    month.add_week(week2)

    assert monthly_load(month) == 780


# ======================================================

def test_empty_month():

    month = MonthlySummary(

        year=2026,

        month=7,

    )

    assert monthly_load(month) == 0