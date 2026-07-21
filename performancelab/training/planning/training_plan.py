"""
PerformanceLab

Training Plan

Container for an athlete's planned workouts.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

from .planned_workout import PlannedWorkout
from .workout_collection import WorkoutCollection


@dataclass
class TrainingPlan(WorkoutCollection):
    """
    Container for an athlete's planned workouts.
    """

    workouts: list[PlannedWorkout] = field(
        default_factory=list,
    )

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