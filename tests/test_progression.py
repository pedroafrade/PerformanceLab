"""
PerformanceLab

Tests for Training Progression.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import WeeklySummary
from performancelab.training.progression import (
    progression,
    distance_progression,
    duration_progression,
    elevation_progression,
    load_progression,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(distance, duration, elevation, rpe):

    workout = Workout()

    workout.info.date = date.today()
    workout.info.distance = distance
    workout.info.duration = duration
    workout.info.elevation_gain = elevation

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def create_week(distance, hours, elevation, rpe):

    week = WeeklySummary(

        start_date=date(2026, 7, 1),

        end_date=date(2026, 7, 7),

    )

    week.history.add(

        create_workout(

            distance,

            timedelta(hours=hours),

            elevation,

            rpe,

        )

    )

    return week


# ======================================================
# Generic
# ======================================================

def test_progression_positive():

    assert progression(100, 120) == 20


def test_progression_negative():

    assert progression(100, 80) == -20


def test_progression_same():

    assert progression(100, 100) == 0


def test_progression_zero():

    assert progression(0, 100) is None


# ======================================================
# Distance
# ======================================================

def test_distance_progression():

    previous = create_week(50, 2, 500, 5)

    current = create_week(60, 2, 500, 5)

    assert distance_progression(previous, current) == 20


# ======================================================
# Duration
# ======================================================

def test_duration_progression():

    previous = create_week(50, 2, 500, 5)

    current = create_week(50, 3, 500, 5)

    assert duration_progression(previous, current) == 50


# ======================================================
# Elevation
# ======================================================

def test_elevation_progression():

    previous = create_week(50, 2, 500, 5)

    current = create_week(50, 2, 750, 5)

    assert elevation_progression(previous, current) == 50


# ======================================================
# Load
# ======================================================

def test_load_progression():

    previous = create_week(50, 2, 500, 5)

    current = create_week(50, 2, 500, 6)

    assert load_progression(previous, current) == 20