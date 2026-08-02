"""
Tests for Workout.
"""
from datetime import datetime, timedelta

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
    
def test_workout_reconciliation_signature():

    workout = Workout()

    workout.info.date = datetime(
        2026,
        8,
        1,
        18,
        30,
    )

    workout.info.sport = " Running "

    workout.info.duration = timedelta(
        minutes=60,
    )

    workout.feedback.estimated_rpe = 5

    assert (
        workout.reconciliation_signature
        == (
            "2026-08-01",
            "running",
            3600.0,
            5.0,
        )
    )


def test_reconciliation_signature_uses_effective_rpe():

    workout = Workout()

    workout.info.date = datetime(
        2026,
        8,
        1,
        18,
        30,
    )

    workout.info.sport = "Running"

    workout.info.duration = timedelta(
        minutes=60,
    )

    workout.feedback.estimated_rpe = 5

    estimated_signature = (
        workout.reconciliation_signature
    )

    workout.feedback.rpe = 7

    confirmed_signature = (
        workout.reconciliation_signature
    )

    assert (
        confirmed_signature
        != estimated_signature
    )

    assert (
        confirmed_signature[-1]
        == 7.0
    )


def test_reconciliation_signature_ignores_title():

    workout = Workout()

    workout.info.date = datetime(
        2026,
        8,
        1,
        18,
        30,
    )

    workout.info.sport = "Running"

    workout.info.duration = timedelta(
        minutes=60,
    )

    workout.feedback.rpe = 6

    original_signature = (
        workout.reconciliation_signature
    )

    workout.info.title = "Updated title"

    assert (
        workout.reconciliation_signature
        == original_signature
    )