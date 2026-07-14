"""
Tests for Workout.
"""

from performancelab.workout import Workout


def test_workout_creation():

    workout = Workout()

    assert workout.info is not None

    assert workout.environment is not None

    assert workout.feedback is not None

    assert workout.sensors is not None


def test_workout_properties():

    workout = Workout()

    workout.info.sport = "Running"

    assert workout.sport == "Running"