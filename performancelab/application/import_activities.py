"""
PerformanceLab

Import activities application use case.
"""

from dataclasses import (
    dataclass,
)
from datetime import (
    date,
    datetime,
)
from collections.abc import (
    Iterable,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.training.planning import (
    TrainingPlanReconciler,
)
from performancelab.workout import (
    Workout,
)

@dataclass(
    frozen=True
)
class ImportedActivityOutcome:
    """
    Factual result for one valid Workout supplied to the use case.
    """

    workout_id: str
    status: str

    def __post_init__(
        self,
    ) -> None:

        if self.status not in (
            "imported",
            "updated",
            "duplicate",
        ):

            raise ValueError(
                "Activity import status must be "
                "imported, updated or duplicate."
            )

@dataclass(
    frozen=True
)
class ImportActivitiesResult:
    """
    Result of importing completed activities.
    """

    athlete: Athlete
    added_count: int
    updated_count: int
    duplicate_count: int
    outcomes: tuple[
        ImportedActivityOutcome,
        ...,
    ]
    reconciled_through: date | None

    @property
    def changed(
        self,
    ) -> bool:
        """
        Return whether the athlete history changed.
        """

        return (
            self.added_count > 0
            or self.updated_count > 0
        )


class ImportActivities:
    """
    Merge completed activities, reconcile and persist once.

    Raw file parsing belongs to importer adapters. This use
    case receives valid Workout objects and coordinates the
    complete change to the Athlete aggregate.
    """

    def __init__(
        self,
        *,
        repository: AthleteRepository,
        reconciler: TrainingPlanReconciler | None = None,
    ) -> None:

        self._repository = repository
        self._reconciler = (
            reconciler
            or TrainingPlanReconciler()
        )

    def execute(
        self,
        athlete_id: str,
        workouts: Iterable[Workout],
    ) -> ImportActivitiesResult:
        """
        Import workouts into an independently loaded athlete.
        """

        athlete = self._repository.get(
            athlete_id
        )

        imported_workouts = tuple(
            workouts
        )

        if not imported_workouts:
            return ImportActivitiesResult(
                athlete=athlete,
                added_count=0,
                updated_count=0,
                duplicate_count=0,
                outcomes=(),
                reconciled_through=None,
            )

        added_count = 0
        updated_count = 0
        duplicate_count = 0

        outcomes: list[
            ImportedActivityOutcome
        ] = []

        imported_days: list[date] = []

        for workout in imported_workouts:

            if not isinstance(
                workout,
                Workout,
            ):
                raise TypeError(
                    "workouts must contain Workout objects."
                )

            merge_result = (
                athlete
                .history
                .merge_with_result(
                    workout
                )
            )

            outcomes.append(
                ImportedActivityOutcome(
                    workout_id=(
                        workout.workout_id
                    ),
                    status=(
                        merge_result.status
                    ),
                )
            )

            if (
                merge_result.status
                == "imported"
            ):

                added_count += 1

            elif (
                merge_result.status
                == "updated"
            ):

                updated_count += 1

            else:

                duplicate_count += 1

            if (
                merge_result.status
                != "duplicate"
            ):

                workout_day = (
                    self._workout_day(
                        workout
                    )
                )

                if workout_day is not None:

                    imported_days.append(
                        workout_day
                    )

        reconciled_through = (
            max(imported_days)
            if imported_days
            else None
        )

        if reconciled_through is not None:

            athlete.training_plan = (
                self._reconciler.reconcile(
                    plan=athlete.training_plan,
                    history=athlete.history,
                    training_state=(
                        athlete
                        .analytics
                        .training_state
                    ),
                    through_day=(
                        reconciled_through
                    ),
                )
            )

        if (
            added_count > 0
            or updated_count > 0
        ):

            self._repository.save(
                athlete
            )

        return ImportActivitiesResult(
            athlete=athlete,
            added_count=added_count,
            updated_count=updated_count,
            duplicate_count=(
                duplicate_count
            ),
            outcomes=tuple(
                outcomes
            ),
            reconciled_through=(
                reconciled_through
            ),
        )

    @staticmethod
    def _workout_day(
        workout: Workout,
    ) -> date | None:
        """
        Return the factual calendar day when available.
        """

        workout_day = workout.date

        if isinstance(
            workout_day,
            datetime,
        ):
            return workout_day.date()

        if isinstance(
            workout_day,
            date,
        ):
            return workout_day

        return None