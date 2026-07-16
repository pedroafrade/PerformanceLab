"""
PerformanceLab

Tests for History.
"""

from datetime import date, datetime

from performancelab.history import History
from performancelab.workout import Workout


# ======================================================
# Empty history
# ======================================================

def test_empty_history():

    history = History()

    assert len(history) == 0


# ======================================================
# Add workout
# ======================================================

def test_add_workout():

    history = History()

    workout = Workout()

    history.add(workout)

    assert len(history) == 1

    assert workout in history


# ======================================================
# Clear history
# ======================================================

def test_clear_history():

    history = History()

    history.add(Workout())

    history.clear()

    assert len(history) == 0


# ======================================================
# Sort workouts
# ======================================================

def test_history_sorts_workouts():

    history = History()

    workout_1 = Workout()
    workout_1.info.date = date(
        2026,
        7,
        10,
    )

    workout_2 = Workout()
    workout_2.info.date = date(
        2026,
        7,
        8,
    )

    history.add(workout_1)
    history.add(workout_2)

    assert history.first is workout_2
    assert history.last is workout_1


# ======================================================
# Sort date and datetime together
# ======================================================

def test_history_sorts_date_and_datetime():

    history = History()

    manual = Workout()
    manual.info.date = date(
        2026,
        7,
        10,
    )

    imported = Workout()
    imported.info.date = datetime(
        2026,
        7,
        8,
        20,
        30,
    )

    history.add(manual)
    history.add(imported)

    assert history.first is imported
    assert history.last is manual