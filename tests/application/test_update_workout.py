from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)

import pytest

from performancelab.application import (
    UpdateWorkout,
    WorkoutUpdate,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.in_memory_athlete_repository import (
    InMemoryAthleteRepository,
)
from performancelab.workout import (
    Workout,
)


class RecordingAthleteRepository(
    InMemoryAthleteRepository
):

    def __init__(
        self,
        athletes=(),
    ) -> None:

        self.save_calls = 0

        super().__init__(
            athletes
        )

        self.save_calls = 0

    def save(
        self,
        athlete,
    ) -> None:

        self.save_calls += 1

        super().save(
            athlete
        )


def workout(
    *,
    workout_id="workout-1",
    workout_date=None,
):

    activity = Workout(
        workout_id=workout_id
    )

    activity.info.title = "Easy Run"
    activity.info.sport = "Running"
    activity.info.sub_sport = "street"
    activity.info.date = (
        workout_date
        or date(
            2026,
            8,
            10,
        )
    )
    activity.info.distance = 10.0
    activity.info.duration = timedelta(
        minutes=50
    )
    activity.info.elevation_gain = 120.0
    activity.feedback.rpe = 5.0

    return activity


def update_data(
    **overrides,
):

    values = {
        "title": "Tempo Run",
        "sport": "Running",
        "sub_sport": "trail",
        "workout_date": date(
            2026,
            8,
            12,
        ),
        "distance": 12.5,
        "duration": timedelta(
            hours=1,
            minutes=5,
            seconds=30,
        ),
        "elevation_gain": 250.0,
        "rpe": 7.0,
    }

    values.update(
        overrides
    )

    return WorkoutUpdate(
        **values
    )


def test_updates_workout_and_saves_once():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        workout()
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = UpdateWorkout(
        repository=repository
    ).execute(
        athlete.athlete_id,
        "workout-1",
        update_data(),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    updated = stored.history[0]

    assert result.changed is True
    assert repository.save_calls == 1
    assert updated.info.title == "Tempo Run"
    assert updated.info.sport == "Running"
    assert (
        updated.info.sub_sport
        == "trail"
    )
    assert updated.info.date == date(
        2026,
        8,
        12,
    )

    assert updated.info.distance == 12.5

    assert updated.info.duration == timedelta(
        hours=1,
        minutes=5,
        seconds=30,
    )

    assert (
        updated.info.elevation_gain
        == 250.0
    )

    assert updated.feedback.rpe == 7.0


def test_identical_update_does_not_save():

    athlete = Athlete(
        name="Pedro"
    )

    activity = workout()

    athlete.history.add(
        activity
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = UpdateWorkout(
        repository=repository
    ).execute(
        athlete.athlete_id,
        activity.workout_id,
        WorkoutUpdate(
            title="Easy Run",
            sport="Running",
            sub_sport="street",
            workout_date=date(
                2026,
                8,
                10,
            ),
            distance=10.0,
            duration=timedelta(
                minutes=50
            ),
            elevation_gain=120.0,
            rpe=5.0,
        ),
    )

    assert result.changed is False
    assert repository.save_calls == 0


def test_preserves_datetime_with_timezone():

    original_time = datetime(
        2026,
        8,
        10,
        11,
        8,
        30,
        tzinfo=timezone.utc,
    )

    updated_time = datetime(
        2026,
        8,
        12,
        11,
        8,
        30,
        tzinfo=timezone.utc,
    )

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        workout(
            workout_date=original_time
        )
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    UpdateWorkout(
        repository=repository
    ).execute(
        athlete.athlete_id,
        "workout-1",
        update_data(
            workout_date=updated_time
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert (
        stored.history[0].info.date
        == updated_time
    )


def test_unknown_workout_does_not_save():

    athlete = Athlete(
        name="Pedro"
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        UpdateWorkout(
            repository=repository
        ).execute(
            athlete.athlete_id,
            "unknown-workout",
            update_data(),
        )

    assert repository.save_calls == 0


def test_invalid_update_does_not_persist():

    athlete = Athlete(
        name="Pedro"
    )

    activity = workout()

    athlete.history.add(
        activity
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="distance cannot be negative",
    ):
        UpdateWorkout(
            repository=repository
        ).execute(
            athlete.athlete_id,
            activity.workout_id,
            update_data(
                distance=-1.0
            ),
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert (
        stored.history[0].distance
        == 10.0
    )
    assert repository.save_calls == 0


def test_invalid_rpe_does_not_persist():

    athlete = Athlete(
        name="Pedro"
    )

    activity = workout()

    athlete.history.add(
        activity
    )

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="rpe must be between 1 and 10",
    ):
        UpdateWorkout(
            repository=repository
        ).execute(
            athlete.athlete_id,
            activity.workout_id,
            update_data(
                rpe=11.0
            ),
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert (
        stored.history[0]
        .feedback.rpe
        == 5.0
    )
    assert repository.save_calls == 0


def test_unknown_athlete_raises():

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        UpdateWorkout(
            repository=(
                RecordingAthleteRepository()
            )
        ).execute(
            "unknown-athlete",
            "workout-1",
            update_data(),
        )