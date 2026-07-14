"""
PerformanceLab

Tests for Volume Analytics.
"""

from datetime import date
from datetime import timedelta

from performancelab.analysis.volume import (
    total_distance,
    total_duration,
    total_elevation,
    average_distance,
    average_duration,
    average_elevation,
)

from performancelab.history import History
from performancelab.workout import Workout


# ======================================================

def create_workout(distance, duration, elevation):

    workout = Workout()

    workout.info.date = date.today()

    workout.info.distance = distance

    workout.info.duration = duration

    workout.info.elevation_gain = elevation

    return workout


# ======================================================

def create_history():

    history = History()

    history.add(

        create_workout(

            10,

            timedelta(hours=1),

            200,

        )

    )

    history.add(

        create_workout(

            20,

            timedelta(hours=2),

            500,

        )

    )

    history.add(

        create_workout(

            15,

            timedelta(hours=1, minutes=30),

            300,

        )

    )

    return history


# ======================================================

def test_total_distance():

    history = create_history()

    assert total_distance(history) == 45


# ======================================================

def test_total_duration():

    history = create_history()

    assert total_duration(history) == timedelta(hours=4, minutes=30)


# ======================================================

def test_total_elevation():

    history = create_history()

    assert total_elevation(history) == 1000


# ======================================================

def test_average_distance():

    history = create_history()

    assert average_distance(history) == 15


# ======================================================

def test_average_duration():

    history = create_history()

    assert average_duration(history) == timedelta(hours=1, minutes=30)


# ======================================================

def test_average_elevation():

    history = create_history()

    assert average_elevation(history) == (200 + 500 + 300) / 3


# ======================================================

def test_empty_history():

    history = History()

    assert total_distance(history) == 0

    assert total_duration(history) == timedelta()

    assert total_elevation(history) == 0

    assert average_distance(history) is None

    assert average_duration(history) is None

    assert average_elevation(history) is None