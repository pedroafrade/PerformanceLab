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

def test_records_normalized_athlete_notes():

    workout = Workout()

    changed = (
        workout.feedback.record_notes(
            "  Mild stiffness after the run.  "
        )
    )

    assert changed is True
    assert workout.feedback.notes == (
        "Mild stiffness after the run."
    )


def test_does_not_change_identical_athlete_notes():

    workout = Workout()

    workout.feedback.notes = (
        "Felt good after the run."
    )

    changed = (
        workout.feedback.record_notes(
            "  Felt good after the run.  "
        )
    )

    assert changed is False
    assert workout.feedback.notes == (
        "Felt good after the run."
    )


def test_can_clear_athlete_notes():

    workout = Workout()

    workout.feedback.notes = (
        "Previous observation."
    )

    changed = (
        workout.feedback.record_notes(
            ""
        )
    )

    assert changed is True
    assert workout.feedback.notes == ""