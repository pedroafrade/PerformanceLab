"""
PerformanceLab

Planned Workout Outcome

Compares a planned workout with the activity performed.
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum

from performancelab.training.load import (
    planned_workout_load,
    workout_load,
)
from performancelab.workout import Workout

from .planned_workout import PlannedWorkout


EQUIVALENT_LOAD_TOLERANCE = 0.20


class WorkoutOutcomeStatus(Enum):
    """
    Relationship between a planned and completed workout.
    """

    PENDING = "pending"
    MISSED = "missed"
    EQUIVALENT = "equivalent"
    MODIFIED = "modified"
    SUBSTITUTE = "substitute"


@dataclass(frozen=True)
class WorkoutOutcome:
    """
    Immutable assessment of one planned workout.
    """

    planned_workout: PlannedWorkout
    completed_workout: Workout | None

    status: WorkoutOutcomeStatus

    planned_load: float | None
    completed_load: float | None

    # ======================================================

    @property
    def load_difference(
        self,
    ) -> float | None:
        """
        Returns completed load minus planned load.
        """

        if (
            self.planned_load is None
            or self.completed_load is None
        ):
            return None

        return (
            self.completed_load
            - self.planned_load
        )


# ======================================================

def _sport_family(
    sport,
) -> str:
    """
    Normalizes sports into comparable training families.
    """

    normalized = str(
        sport or ""
    ).strip().lower()

    if any(
        token in normalized
        for token in (
            "run",
            "running",
            "trail",
            "jog",
        )
    ):
        return "running"

    if any(
        token in normalized
        for token in (
            "cycl",
            "bike",
            "bicycle",
        )
    ):
        return "cycling"

    if "swim" in normalized:
        return "swimming"

    return normalized or "other"


# ======================================================

def assess_workout_outcome(
    *,
    planned_workout: PlannedWorkout,
    completed_workout: Workout | None,
    reference_day: date,
) -> WorkoutOutcome:
    """
    Compares one planned workout with the activity performed
    on that day.
    """

    if not isinstance(
        planned_workout,
        PlannedWorkout,
    ):
        raise TypeError(
            "planned_workout must be a "
            "PlannedWorkout."
        )

    if (
        completed_workout is not None
        and not isinstance(
            completed_workout,
            Workout,
        )
    ):
        raise TypeError(
            "completed_workout must be a "
            "Workout or None."
        )

    if not isinstance(
        reference_day,
        date,
    ):
        raise TypeError(
            "reference_day must be a date."
        )

    planned_load = planned_workout_load(
        planned_workout
    )

    if completed_workout is None:

        status = (
            WorkoutOutcomeStatus.MISSED
            if planned_workout.day
            < reference_day
            else WorkoutOutcomeStatus.PENDING
        )

        return WorkoutOutcome(
            planned_workout=planned_workout,
            completed_workout=None,
            status=status,
            planned_load=planned_load,
            completed_load=None,
        )

    completed_load = workout_load(
        completed_workout
    )

    same_sport_family = (
        _sport_family(
            planned_workout.sport
        )
        == _sport_family(
            completed_workout.sport
        )
    )

    loads_are_equivalent = False

    if (
        planned_load is not None
        and planned_load > 0
        and completed_load is not None
    ):
        relative_difference = abs(
            completed_load
            - planned_load
        ) / planned_load

        loads_are_equivalent = (
            relative_difference
            <= EQUIVALENT_LOAD_TOLERANCE
        )

    if not same_sport_family:

        status = (
            WorkoutOutcomeStatus.SUBSTITUTE
        )

    elif loads_are_equivalent:

        status = (
            WorkoutOutcomeStatus.EQUIVALENT
        )

    else:

        status = (
            WorkoutOutcomeStatus.MODIFIED
        )

    return WorkoutOutcome(
        planned_workout=planned_workout,
        completed_workout=completed_workout,
        status=status,
        planned_load=planned_load,
        completed_load=completed_load,
    )