"""
PerformanceLab

Tests for History.
"""

from datetime import date, datetime, timedelta

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

# ======================================================

def create_identifiable_workout(
    workout_date,
    *,
    distance=10.0,
    duration=timedelta(hours=1),
):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.sport = "Running"
    workout.info.distance = distance
    workout.info.duration = duration

    return workout


def test_history_finds_matching_workout():

    history = History()

    existing = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            8,
            0,
        )
    )

    candidate = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            8,
            3,
        ),
        distance=10.05,
        duration=timedelta(
            hours=1,
            seconds=30,
        ),
    )

    history.add(existing)

    assert (
        history.find_matching(candidate)
        is existing
    )


def test_history_does_not_match_different_workout():

    history = History()

    existing = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            8,
            0,
        )
    )

    candidate = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            18,
            0,
        )
    )

    history.add(existing)

    assert (
        history.find_matching(candidate)
        is None
    )

def test_history_merges_matching_workout():

    history = History()

    existing = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            8,
            0,
        )
    )

    existing.feedback.rpe = 6

    imported = create_identifiable_workout(
        datetime(
            2026,
            7,
            20,
            8,
            2,
        ),
        distance=10.05,
        duration=timedelta(
            hours=1,
            seconds=20,
        ),
    )

    imported.feedback.estimated_rpe = 7.5

    imported.sensors.add(
        "heart_rate",
        [
            {
                "value": 150,
            },
        ],
    )

    history.add(existing)

    stored, added = history.merge(
        imported
    )

    assert added is False
    assert stored is existing
    assert len(history) == 1

    assert (
        existing.feedback.rpe
        == 6
    )

    assert (
        existing.feedback.estimated_rpe
        == 7.5
    )

    assert (
        existing.feedback.effective_rpe
        == 6
    )

    assert (
        existing.sensors.get(
            "heart_rate"
        )
        == [
            {
                "value": 150,
            },
        ]
    )