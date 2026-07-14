"""
PerformanceLab

Tests for WeeklySummary.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import WeeklySummary


# ======================================================
# Helpers
# ======================================================

def create_workout(
    sport,
    workout_date,
    distance,
    duration,
    elevation,
):

    workout = Workout()

    workout.info.sport = sport
    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = elevation

    return workout


# ======================================================
# Tests
# ======================================================

def test_empty_week():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),
        end_date=date(2026, 7, 12),

    )

    assert week.workouts == 0
    assert week.training_days == 0
    assert week.duration == timedelta()
    assert week.sports == []


# ======================================================

def test_week_workouts():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),
        end_date=date(2026, 7, 12),

    )

    week.history.add(

        create_workout(

            "Running",
            date(2026, 7, 7),
            10,
            timedelta(hours=1),
            200,

        )

    )

    week.history.add(

        create_workout(

            "Cycling",
            date(2026, 7, 8),
            50,
            timedelta(hours=2),
            600,

        )

    )

    assert week.workouts == 2
    assert week.training_days == 2
    assert week.duration == timedelta(hours=3)


# ======================================================

def test_group_by_sport():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),
        end_date=date(2026, 7, 12),

    )

    week.history.add(

        create_workout(

            "Running",
            date(2026, 7, 7),
            10,
            timedelta(hours=1),
            200,

        )

    )

    week.history.add(

        create_workout(

            "Running",
            date(2026, 7, 8),
            15,
            timedelta(hours=1, minutes=20),
            300,

        )

    )

    week.history.add(

        create_workout(

            "Cycling",
            date(2026, 7, 9),
            60,
            timedelta(hours=2),
            800,

        )

    )

    assert len(week.by_sport["Running"]) == 2
    assert len(week.by_sport["Cycling"]) == 1


# ======================================================

def test_history_for_sport():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),
        end_date=date(2026, 7, 12),

    )

    week.history.add(

        create_workout(

            "Running",
            date(2026, 7, 7),
            10,
            timedelta(hours=1),
            200,

        )

    )

    running = week.history_for("Running")
    cycling = week.history_for("Cycling")

    assert len(running) == 1
    assert len(cycling) == 0