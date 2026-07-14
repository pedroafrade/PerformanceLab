"""
PerformanceLab

Tests for MonthlySummary.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import WeeklySummary
from performancelab.training.monthly import MonthlySummary


# ======================================================
# Helpers
# ======================================================

def create_workout(workout_date, sport="Running"):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.sport = sport
    workout.info.distance = 10
    workout.info.duration = timedelta(hours=1)

    return workout


def create_week(start_date):

    week = WeeklySummary(

        start_date=start_date,

        end_date=start_date + timedelta(days=6),

    )

    return week


# ======================================================
# Tests
# ======================================================

def test_empty_month():

    month = MonthlySummary(2026, 7)

    assert month.year == 2026
    assert month.month == 7
    assert month.workouts == 0
    assert month.training_days == 0
    assert month.duration == timedelta()
    assert month.sports == []


# ======================================================

def test_add_week():

    month = MonthlySummary(2026, 7)

    week = create_week(date(2026, 7, 6))

    month.add_week(week)

    assert len(month.weeks) == 1


# ======================================================

def test_workouts():

    month = MonthlySummary(2026, 7)

    week1 = create_week(date(2026, 7, 6))
    week2 = create_week(date(2026, 7, 13))

    week1.history.add(create_workout(date(2026, 7, 6)))
    week1.history.add(create_workout(date(2026, 7, 7)))

    week2.history.add(create_workout(date(2026, 7, 14)))

    month.add_week(week1)
    month.add_week(week2)

    assert month.workouts == 3


# ======================================================

def test_training_days():

    month = MonthlySummary(2026, 7)

    week1 = create_week(date(2026, 7, 6))
    week2 = create_week(date(2026, 7, 13))

    week1.history.add(create_workout(date(2026, 7, 6)))
    week1.history.add(create_workout(date(2026, 7, 7)))

    week2.history.add(create_workout(date(2026, 7, 14)))

    month.add_week(week1)
    month.add_week(week2)

    assert month.training_days == 3


# ======================================================

def test_duration():

    month = MonthlySummary(2026, 7)

    week = create_week(date(2026, 7, 6))

    week.history.add(create_workout(date(2026, 7, 6)))
    week.history.add(create_workout(date(2026, 7, 7)))

    month.add_week(week)

    assert month.duration == timedelta(hours=2)


# ======================================================

def test_sports():

    month = MonthlySummary(2026, 7)

    week = create_week(date(2026, 7, 6))

    week.history.add(

        create_workout(

            date(2026, 7, 6),

            "Running",

        )

    )

    week.history.add(

        create_workout(

            date(2026, 7, 7),

            "Cycling",

        )

    )

    month.add_week(week)

    assert month.sports == [

        "Cycling",

        "Running",

    ]


# ======================================================

def test_repr():

    month = MonthlySummary(2026, 7)

    assert "MonthlySummary" in repr(month)