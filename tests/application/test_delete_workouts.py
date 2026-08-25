from datetime import (
    date,
    datetime,
    timedelta,
)

import pytest

from performancelab.application import (
    DeleteWorkouts,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.activity_coach_records import (
    ActivityCoachInterpretation,
)
from performancelab.coaching import (
    ActivityCoachNarrative,
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
    workout_id,
    *,
    day,
):

    activity = Workout(
        workout_id=workout_id
    )

    activity.info.title = (
        f"Workout {workout_id}"
    )
    activity.info.sport = "Running"
    activity.info.date = day
    activity.info.distance = 10.0
    activity.info.duration = timedelta(
        minutes=60
    )

    return activity


def athlete_with_workouts():

    athlete = Athlete(
        name="Pedro"
    )

    athlete.history.add(
        workout(
            "workout-1",
            day=date(
                2026,
                8,
                10,
            ),
        )
    )

    athlete.history.add(
        workout(
            "workout-2",
            day=date(
                2026,
                8,
                12,
            ),
        )
    )

    athlete.history.add(
        workout(
            "workout-3",
            day=date(
                2026,
                8,
                14,
            ),
        )
    )
    athlete.activity_coach_interpretations.add(
        ActivityCoachInterpretation(
            workout_id="workout-2",
            contract_version=(
                "activity-coach-v1"
            ),
            context_hash="context-2",
            generated_at=datetime(
                2026,
                8,
                12,
                14,
                0,
            ),
            narrative=(
                ActivityCoachNarrative(
                    measured_facts="Facts.",
                    deterministic_signals=(
                        "Signals."
                    ),
                    prudent_interpretation=(
                        "Interpretation."
                    ),
                    recommendations=(
                        "Recommendation."
                    ),
                    data_limitations=(
                        "Limitations."
                    ),
                    provider="google-gemini",
                    model=(
                        "gemini-3.5-flash"
                    ),
                )
            ),
        )
    )
    return athlete


def test_deletes_one_workout_and_saves_once():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = DeleteWorkouts(
        repository=repository
    ).execute(
        athlete.athlete_id,
        (
            "workout-2",
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    stored_ids = tuple(
        workout.workout_id
        for workout in stored.history
    )

    assert result.changed is True
    assert result.removed_count == 1
    assert (
        result
        .removed_interpretation_count
        == 1
    )

    assert len(
        stored
        .activity_coach_interpretations
    ) == 0
    assert (
        result.removed_workout_ids
        == (
            "workout-2",
        )
    )

    assert stored_ids == (
        "workout-1",
        "workout-3",
    )

    assert repository.save_calls == 1


def test_deletes_multiple_workouts_and_saves_once():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = DeleteWorkouts(
        repository=repository
    ).execute(
        athlete.athlete_id,
        (
            "workout-1",
            "workout-3",
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.removed_count == 2
    assert len(stored.history) == 1

    assert (
        stored.history[0].workout_id
        == "workout-2"
    )

    assert repository.save_calls == 1


def test_duplicate_ids_remove_workout_once():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = DeleteWorkouts(
        repository=repository
    ).execute(
        athlete.athlete_id,
        (
            "workout-1",
            "workout-1",
        ),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.removed_count == 1
    assert len(stored.history) == 2
    assert repository.save_calls == 1


def test_empty_request_does_not_save():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    result = DeleteWorkouts(
        repository=repository
    ).execute(
        athlete.athlete_id,
        (),
    )

    stored = repository.get(
        athlete.athlete_id
    )

    assert result.changed is False
    assert result.removed_count == 0
    assert len(stored.history) == 3
    assert repository.save_calls == 0


def test_missing_workout_prevents_complete_deletion():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        KeyError,
        match="missing-workout",
    ):
        DeleteWorkouts(
            repository=repository
        ).execute(
            athlete.athlete_id,
            (
                "workout-1",
                "missing-workout",
            ),
        )

    stored = repository.get(
        athlete.athlete_id
    )

    stored_ids = tuple(
        workout.workout_id
        for workout in stored.history
    )

    assert stored_ids == (
        "workout-1",
        "workout-2",
        "workout-3",
    )

    assert repository.save_calls == 0


def test_rejects_single_string_as_collection():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        TypeError,
        match="not a single string",
    ):
        DeleteWorkouts(
            repository=repository
        ).execute(
            athlete.athlete_id,
            "workout-1",
        )

    assert repository.save_calls == 0


def test_rejects_invalid_identifier_before_deletion():

    athlete = athlete_with_workouts()

    repository = (
        RecordingAthleteRepository(
            (
                athlete,
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        DeleteWorkouts(
            repository=repository
        ).execute(
            athlete.athlete_id,
            (
                "workout-1",
                " ",
            ),
        )

    stored = repository.get(
        athlete.athlete_id
    )

    assert len(stored.history) == 3
    assert repository.save_calls == 0


def test_unknown_athlete_raises():

    with pytest.raises(
        FileNotFoundError,
        match="does not exist",
    ):
        DeleteWorkouts(
            repository=(
                RecordingAthleteRepository()
            )
        ).execute(
            "unknown-athlete",
            (
                "workout-1",
            ),
        )