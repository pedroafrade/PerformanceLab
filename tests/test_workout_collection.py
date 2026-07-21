from datetime import date, datetime, timedelta

from performancelab.training.planning import (
    PlannedWorkout,
    WorkoutCollection,
)


class DummyCollection(WorkoutCollection):

    def __init__(self, workouts):

        self.workouts = workouts


def workout(
    day,
    hour,
    duration=60,
    distance=10.0,
):

    return PlannedWorkout(
        scheduled_at=datetime.combine(
            day,
            datetime.min.time(),
        ) + timedelta(hours=hour),
        sport="Run",
        duration=timedelta(minutes=duration),
        distance=distance,
    )


def rest(day):

    return PlannedWorkout(
        scheduled_at=datetime.combine(
            day,
            datetime.min.time(),
        )
    )


def test_for_day():

    monday = date(2025, 1, 6)
    tuesday = date(2025, 1, 7)

    collection = DummyCollection(
        [
            workout(monday, 8),
            workout(monday, 18),
            workout(tuesday, 9),
        ]
    )

    result = collection.for_day(monday)

    assert len(result) == 2


def test_next_workout():

    monday = date(2025, 1, 6)

    morning = workout(monday, 8)
    evening = workout(monday, 18)

    collection = DummyCollection(
        [
            morning,
            evening,
        ]
    )

    assert collection.next_workout(
        datetime(2025, 1, 6, 9)
    ) is evening


def test_next_workout_none():

    monday = date(2025, 1, 6)

    collection = DummyCollection(
        [
            workout(monday, 8),
        ]
    )

    assert collection.next_workout(
        datetime(2025, 1, 7)
    ) is None


def test_training_days():

    monday = date(2025, 1, 6)
    tuesday = date(2025, 1, 7)

    collection = DummyCollection(
        [
            workout(monday, 8),
            workout(monday, 18),
            rest(tuesday),
        ]
    )

    assert collection.training_days == 1


def test_total_duration():

    monday = date(2025, 1, 6)

    collection = DummyCollection(
        [
            workout(monday, 8, duration=30),
            workout(monday, 18, duration=90),
        ]
    )

    assert collection.total_duration == timedelta(
        minutes=120,
    )


def test_total_distance():

    monday = date(2025, 1, 6)

    collection = DummyCollection(
        [
            workout(monday, 8, distance=5),
            workout(monday, 18, distance=12.5),
        ]
    )

    assert collection.total_distance == 17.5


def test_len():

    monday = date(2025, 1, 6)

    collection = DummyCollection(
        [
            workout(monday, 8),
            workout(monday, 18),
        ]
    )

    assert len(collection) == 2


def test_iter():

    monday = date(2025, 1, 6)

    workouts = [
        workout(monday, 8),
        workout(monday, 18),
    ]

    collection = DummyCollection(workouts)

    assert list(collection) == workouts