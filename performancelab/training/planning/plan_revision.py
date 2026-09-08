"""
PerformanceLab

Immutable training-plan revision snapshots.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import uuid4

from .planned_workout import PlannedWorkout


PLAN_REVISION_SOURCES = {
    "generated",
    "automatic_adaptation",
    "manual_edit",
    "recovery",
}


@dataclass(frozen=True, slots=True)
class TrainingPlanRevision:
    """
    One immutable, recoverable version of a training plan.

    ``workouts`` is a complete snapshot. This intentionally
    keeps recovery independent from the adaptation UI and
    also supports future Plan Builder edits.
    """

    created_on: date
    source: str
    workouts: tuple[PlannedWorkout, ...]

    reason: str = ""
    parent_revision_id: str | None = None
    revision_id: str = field(
        default_factory=lambda: str(uuid4()),
    )

    def __post_init__(self) -> None:

        if (
            not isinstance(self.created_on, date)
            or isinstance(self.created_on, datetime)
        ):
            raise TypeError("created_on must be a date.")

        if self.source not in PLAN_REVISION_SOURCES:
            raise ValueError(
                "source must describe a supported plan "
                "revision origin."
            )

        if not isinstance(self.workouts, tuple):
            raise TypeError("workouts must be a tuple.")

        if not all(
            isinstance(workout, PlannedWorkout)
            for workout in self.workouts
        ):
            raise TypeError(
                "workouts must contain PlannedWorkout objects."
            )

        if (
            not isinstance(self.revision_id, str)
            or not self.revision_id.strip()
        ):
            raise ValueError(
                "revision_id must be a non-empty string."
            )

        if (
            self.parent_revision_id is not None
            and (
                not isinstance(self.parent_revision_id, str)
                or not self.parent_revision_id.strip()
            )
        ):
            raise ValueError(
                "parent_revision_id must be a non-empty "
                "string or None."
            )
