"""
PerformanceLab

Tests for Time Analytics.
"""

from datetime import date
from datetime import timedelta

from performancelab.analysis.time import workouts_between
from performancelab.analysis.time import distance_between
from performancelab.analysis.time import duration_between
from performancelab.analysis.time import elevation_between
from performancelab.analysis.time import average_rpe_between
from performancelab.analysis.time import training_days_between

from performancelab.history import History
from performancelab.workout import Workout


# ======================================================

def create_workout(
    workout_date,
    distance,
    duration,
    elevation,
    rpe,
):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.distance = distance
    workout.info.duration = duration

    workout.info.elevation_gain = elevation

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def create_history():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 1),

            10,

            timedelta(hours=1),

            200,

            6,

        )

    )

    history.add(

        create_workout(

            date(2026, 7, 2),

            20,

            timedelta(hours=2),

            500,

            8,

        )

    )

    history.add(

        create_workout(

            date(2026, 7, 10),

            15,

            timedelta(hours=1, minutes=30),

            300,

            7,

        )

    )

    return history


# ======================================================

def test_workouts_between():

    history = create_history()

    workouts = workouts_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert len(workouts) == 2


# ======================================================

def test_distance_between():

    history = create_history()

    total = distance_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert total == 30


# ======================================================

def test_duration_between():

    history = create_history()

    total = duration_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert total == timedelta(hours=3)


# ======================================================

def test_elevation_between():

    history = create_history()

    total = elevation_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert total == 700


# ======================================================

def test_average_rpe_between():

    history = create_history()

    average = average_rpe_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert average == 7


# ======================================================

def test_training_days_between():

    history = create_history()

    days = training_days_between(

        history,

        date(2026, 7, 1),

        date(2026, 7, 5),

    )

    assert days == 2


# ======================================================

def test_empty_period():

    history = create_history()

    assert workouts_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) == []

    assert distance_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) == 0

    assert duration_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) == timedelta()

    assert elevation_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) == 0

    assert average_rpe_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) is None

    assert training_days_between(

        history,

        date(2026, 8, 1),

        date(2026, 8, 31),

    ) == 0