"""
PerformanceLab

Delete workouts application use case.
"""

from collections.abc import (
    Iterable,
)
from dataclasses import (
    dataclass,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.workout import (
    Workout,
)


@dataclass(
    frozen=True
)
class DeleteWorkoutsResult:
    """
    Result of deleting completed workouts.
    """

    athlete: Athlete
    removed_workout_ids: tuple[str, ...]
    removed_interpretation_count: int = 0

    @property
    def removed_count(
        self,
    ) -> int:
        """
        Return the number of removed workouts.
        """

        return len(
            self.removed_workout_ids
        )

    @property
    def changed(
        self,
    ) -> bool:
        """
        Return whether any workout was removed.
        """

        return self.removed_count > 0


class DeleteWorkouts:
    """
    Delete completed workouts and persist once.

    Every requested workout is resolved before mutation.
    A missing workout therefore prevents the complete
    operation without changing persisted data.
    """

    def __init__(
        self,
        *,
        repository: AthleteRepository,
    ) -> None:

        self._repository = repository

    def execute(
        self,
        athlete_id: str,
        workout_ids: Iterable[str],
    ) -> DeleteWorkoutsResult:
        """
        Delete the requested workouts atomically.
        """

        if not isinstance(
            athlete_id,
            str,
        ) or not athlete_id.strip():
            raise ValueError(
                "athlete_id is required."
            )

        normalized_ids = (
            self._normalize_workout_ids(
                workout_ids
            )
        )

        athlete = self._repository.get(
            athlete_id
        )

        if not normalized_ids:

            return DeleteWorkoutsResult(
                athlete=athlete,
                removed_workout_ids=(),
            )

        workouts = self._find_workouts(
            athlete,
            normalized_ids,
        )

        removed_count = (
            athlete.history.remove_many(
                workouts
            )
        )

        if removed_count != len(
            workouts
        ):
            raise RuntimeError(
                "Workout deletion was incomplete."
            )

        removed_interpretation_count = (
            athlete
            .activity_coach_interpretations
            .remove_for_workouts(
                normalized_ids
            )
        )

        self._repository.save(
            athlete
        )

        return DeleteWorkoutsResult(
            athlete=athlete,
            removed_workout_ids=(
                normalized_ids
            ),
            removed_interpretation_count=(
                removed_interpretation_count
            ),
        )

    @staticmethod
    def _normalize_workout_ids(
        workout_ids: Iterable[str],
    ) -> tuple[str, ...]:
        """
        Validate and deduplicate workout identifiers.
        """

        if isinstance(
            workout_ids,
            str,
        ):
            raise TypeError(
                "workout_ids must be an iterable "
                "of strings, not a single string."
            )

        try:
            requested_ids = tuple(
                workout_ids
            )

        except TypeError as error:
            raise TypeError(
                "workout_ids must be iterable."
            ) from error

        normalized_ids: list[str] = []

        for workout_id in requested_ids:

            if not isinstance(
                workout_id,
                str,
            ):
                raise TypeError(
                    "workout_ids must contain strings."
                )

            normalized_id = (
                workout_id.strip()
            )

            if not normalized_id:
                raise ValueError(
                    "workout_id cannot be empty."
                )

            if (
                normalized_id
                not in normalized_ids
            ):
                normalized_ids.append(
                    normalized_id
                )

        return tuple(
            normalized_ids
        )

    @staticmethod
    def _find_workouts(
        athlete: Athlete,
        workout_ids: tuple[str, ...],
    ) -> tuple[Workout, ...]:
        """
        Resolve every requested workout before deletion.
        """

        workouts_by_id = {
            workout.workout_id: workout
            for workout in athlete.history
        }

        missing_ids = tuple(
            workout_id
            for workout_id in workout_ids
            if workout_id not in workouts_by_id
        )

        if missing_ids:

            missing_list = ", ".join(
                repr(workout_id)
                for workout_id in missing_ids
            )

            raise KeyError(
                "Workouts do not exist for athlete "
                f"{athlete.athlete_id!r}: "
                f"{missing_list}."
            )

        return tuple(
            workouts_by_id[
                workout_id
            ]
            for workout_id in workout_ids
        )