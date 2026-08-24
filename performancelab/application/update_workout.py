"""
PerformanceLab

Update workout application use case.
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    date,
    datetime,
    timedelta,
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
class WorkoutUpdate:
    """
    Validated editable values for one completed workout.
    """

    title: str
    sport: str
    sub_sport: str
    workout_date: date | datetime
    distance: float | None
    duration: timedelta
    elevation_gain: float
    rpe: float | None


@dataclass(
    frozen=True
)
class UpdateWorkoutResult:
    """
    Result of updating one completed workout.
    """

    athlete: Athlete
    workout: Workout
    changed: bool


class UpdateWorkout:
    """
    Update and persist one completed workout atomically.
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
        workout_id: str,
        update: WorkoutUpdate,
    ) -> UpdateWorkoutResult:
        """
        Validate and apply an update to one workout.
        """

        self._validate_identifiers(
            athlete_id=athlete_id,
            workout_id=workout_id,
        )

        self._validate_update(
            update
        )

        athlete = self._repository.get(
            athlete_id
        )

        workout = self._find_workout(
            athlete,
            workout_id,
        )

        current_values = self._values(
            workout
        )

        requested_values = (
            update.title.strip(),
            update.sport.strip(),
            update.sub_sport.strip(),
            update.workout_date,
            update.distance,
            update.duration,
            update.elevation_gain,
            update.rpe,
        )

        if current_values == requested_values:

            return UpdateWorkoutResult(
                athlete=athlete,
                workout=workout,
                changed=False,
            )

        workout.info.title = (
            requested_values[0]
        )
        workout.info.sport = (
            requested_values[1]
        )
        workout.info.sub_sport = (
            requested_values[2]
        )
        workout.info.date = (
            requested_values[3]
        )
        workout.info.distance = (
            requested_values[4]
        )
        workout.info.duration = (
            requested_values[5]
        )
        workout.info.elevation_gain = (
            requested_values[6]
        )
        workout.feedback.rpe = (
            requested_values[7]
        )

        athlete.history._sort()

        self._repository.save(
            athlete
        )

        return UpdateWorkoutResult(
            athlete=athlete,
            workout=workout,
            changed=True,
        )

    @staticmethod
    def _validate_identifiers(
        *,
        athlete_id: str,
        workout_id: str,
    ) -> None:
        """
        Validate the aggregate and workout identifiers.
        """

        if not str(
            athlete_id
        ).strip():
            raise ValueError(
                "athlete_id is required."
            )

        if not str(
            workout_id
        ).strip():
            raise ValueError(
                "workout_id is required."
            )

    @staticmethod
    def _validate_update(
        update: WorkoutUpdate,
    ) -> None:
        """
        Validate every value before changing the athlete.
        """

        if not isinstance(
            update,
            WorkoutUpdate,
        ):
            raise TypeError(
                "update must be a WorkoutUpdate."
            )

        if not isinstance(
            update.title,
            str,
        ):
            raise TypeError(
                "title must be a string."
            )

        if not isinstance(
            update.sport,
            str,
        ):
            raise TypeError(
                "sport must be a string."
            )

        if not update.sport.strip():
            raise ValueError(
                "sport is required."
            )

        if not isinstance(
            update.sub_sport,
            str,
        ):
            raise TypeError(
                "sub_sport must be a string."
            )

        if not isinstance(
            update.workout_date,
            date,
        ):
            raise TypeError(
                "workout_date must be a date or datetime."
            )

        if (
            update.distance is not None
            and update.distance < 0
        ):
            raise ValueError(
                "distance cannot be negative."
            )

        if not isinstance(
            update.duration,
            timedelta,
        ):
            raise TypeError(
                "duration must be a timedelta."
            )

        if update.duration < timedelta():
            raise ValueError(
                "duration cannot be negative."
            )

        if update.elevation_gain < 0:
            raise ValueError(
                "elevation_gain cannot be negative."
            )

        if (
            update.rpe is not None
            and not 1 <= update.rpe <= 10
        ):
            raise ValueError(
                "rpe must be between 1 and 10."
            )

    @staticmethod
    def _find_workout(
        athlete: Athlete,
        workout_id: str,
    ) -> Workout:
        """
        Find a workout belonging to the loaded athlete.
        """

        for workout in athlete.history:

            if (
                workout.workout_id
                == workout_id
            ):
                return workout

        raise KeyError(
            f"Workout {workout_id!r} does not exist "
            f"for athlete {athlete.athlete_id!r}."
        )

    @staticmethod
    def _values(
        workout: Workout,
    ) -> tuple[
        str,
        str,
        str,
        date | datetime | None,
        float | None,
        timedelta | None,
        float | None,
        float | None,
    ]:
        """
        Return the editable values currently persisted.
        """

        return (
            str(
                workout.info.title
                or ""
            ).strip(),
            str(
                workout.info.sport
                or ""
            ).strip(),
            str(
                workout.info.sub_sport
                or ""
            ).strip(),
            workout.info.date,
            workout.info.distance,
            workout.info.duration,
            workout.info.elevation_gain,
            workout.feedback.rpe,
        )