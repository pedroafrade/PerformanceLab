"""
PerformanceLab

Training Plan

Container for an athlete's planned workouts.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from .planned_workout import PlannedWorkout
from .workout_collection import WorkoutCollection

from uuid import uuid4

@dataclass
class TrainingPlan(WorkoutCollection):
    """
    Container for an athlete's planned workouts.
    """
    plan_id: str = field(
        default_factory=lambda: str(
            uuid4()
        ),
    )

    start_date: date | None = None
    end_date: date | None = None

    workouts: list[PlannedWorkout] = field(
        default_factory=list,
    )

    # ======================================================

    def __post_init__(self) -> None:

        if (
            not isinstance(self.plan_id, str)
            or not self.plan_id.strip()
        ):
            raise ValueError(
                "plan_id must be a non-empty string."
            )

        has_start = self.start_date is not None
        has_end = self.end_date is not None

        if has_start != has_end:
            raise ValueError(
                "TrainingPlan requires both start_date "
                "and end_date."
            )

        if has_start:

            if (
                not isinstance(self.start_date, date)
                or isinstance(
                    self.start_date,
                    datetime,
                )
            ):
                raise TypeError(
                    "start_date must be a date."
                )

            if (
                not isinstance(self.end_date, date)
                or isinstance(
                    self.end_date,
                    datetime,
                )
            ):
                raise TypeError(
                    "end_date must be a date."
                )

            if self.end_date < self.start_date:
                raise ValueError(
                    "end_date cannot be before start_date."
                )

        for workout in self.workouts:

            if not isinstance(
                workout,
                PlannedWorkout,
            ):
                raise TypeError(
                    "workouts must contain PlannedWorkout "
                    "objects."
                )

            self._validate_workout_horizon(
                workout
            )

        self._sort()
    # ======================================================

    def schedule(
        self,
        scheduled_at: datetime,
        sport: str | None = None,
        title: str | None = None,
        duration: timedelta | None = None,
        distance: float | None = None,
        description: str | None = None,
        intensity: str | None = None,
        objective: str | None = None,
        structure: tuple[str, ...] = (),
        equipment: tuple[str, ...] = (),
    ) -> PlannedWorkout:

        workout = PlannedWorkout(
            scheduled_at=scheduled_at,
            sport=sport,
            title=title,
            duration=duration,
            distance=distance,
            description=description,
            intensity=intensity,
            objective=objective,
            structure=structure,
            equipment=equipment,
        )

        self.add(workout)

        return workout

    # ======================================================

    def add(
        self,
        workout: PlannedWorkout,
    ) -> None:

        if not isinstance(
            workout,
            PlannedWorkout,
        ):

            raise TypeError(
                "workout must be a PlannedWorkout."
            )

        self._validate_workout_horizon(
            workout
        )

        self.workouts.append(workout)

        self._sort()

    # ======================================================

    def remove(
        self,
        workout: PlannedWorkout,
    ) -> None:

        if workout in self.workouts:

            self.workouts.remove(workout)

    # ======================================================

    def clear(self) -> None:

        self.workouts.clear()
    # ======================================================

    def covers(
        self,
        day: date,
    ) -> bool:
        """
        Returns whether a calendar day belongs to the
        complete training-plan horizon.
        """

        if (
            self.start_date is None
            or self.end_date is None
        ):
            return False

        return (
            self.start_date
            <= day
            <= self.end_date
        )

    # ======================================================

    def _validate_workout_horizon(
        self,
        workout: PlannedWorkout,
    ) -> None:

        if (
            self.start_date is None
            or self.end_date is None
        ):
            return

        workout_day = workout.day

        if (
            workout_day is None
            or not self.covers(workout_day)
        ):
            raise ValueError(
                "Workout date is outside the "
                "TrainingPlan horizon."
            )
    # ======================================================

    @staticmethod
    def _sortable_date(
        value,
    ) -> datetime:

        if value is None:

            return datetime.max

        if isinstance(
            value,
            datetime,
        ):

            return value.replace(
                tzinfo=None,
            )

        if isinstance(
            value,
            date,
        ):

            return datetime.combine(
                value,
                time.min,
            )

        raise TypeError(
            "Planned workout date must be a "
            "date, datetime or None."
        )

    # ======================================================

    def _sort(self) -> None:

        self.workouts.sort(
            key=lambda workout: self._sortable_date(
                workout.scheduled_at
            )
        )

    # ======================================================

    @property
    def first(
        self,
    ) -> PlannedWorkout | None:

        if not self.workouts:

            return None

        return self.workouts[0]

    # ======================================================

    @property
    def last(
        self,
    ) -> PlannedWorkout | None:

        if not self.workouts:

            return None

        return self.workouts[-1]


    # ======================================================

    def __getitem__(
        self,
        index,
    ):

        return self.workouts[index]

    # ======================================================

    def __contains__(
        self,
        workout,
    ) -> bool:

        return workout in self.workouts

    # ======================================================

    def __repr__(self) -> str:

        return (
            "TrainingPlan("
            f"{len(self.workouts)} workouts)"
        )