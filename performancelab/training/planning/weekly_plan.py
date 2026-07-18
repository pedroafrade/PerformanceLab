"""
PerformanceLab

Weekly Plan

Represents one planned training week.
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Iterable


@dataclass(frozen=True)
class PlannedWorkout:
    """
    Represents one planned workout.
    """

    scheduled_at: datetime

    sport: str | None = None
    title: str | None = None

    duration: timedelta | None = None
    distance: float | None = None

    description: str | None = None
    intensity: str | None = None
    objective: str | None = None

    structure: tuple[str, ...] = ()
    equipment: tuple[str, ...] = ()

    # ======================================================

    @property
    def day(self):

        return self.scheduled_at.date()

    # ======================================================

    @property
    def is_rest(self):

        return (
            self.sport is None
            and self.title is None
            and self.duration is None
            and self.distance is None
        )

    # ======================================================

    def __repr__(self):

        return (
            "PlannedWorkout("
            f"{self.scheduled_at.isoformat()}, "
            f"sport={self.sport!r}, "
            f"title={self.title!r})"
        )


@dataclass
class WeeklyPlan:
    """
    Represents one planned training week.
    """

    start_date: date
    end_date: date

    workouts: list[PlannedWorkout] = field(
        default_factory=list,
    )

    # ======================================================

    def __post_init__(self):

        expected_end = self.start_date + timedelta(
            days=6,
        )

        if self.end_date != expected_end:

            raise ValueError(
                "WeeklyPlan must represent exactly seven days."
            )

        self.workouts.sort(
            key=lambda workout: workout.scheduled_at,
        )

    # ======================================================

    def add(self, workout: PlannedWorkout):

        if not isinstance(workout, PlannedWorkout):

            raise TypeError(
                "workout must be a PlannedWorkout."
            )

        if not (
            self.start_date
            <= workout.day
            <= self.end_date
        ):

            raise ValueError(
                "Workout date is outside this weekly plan."
            )

        self.workouts.append(workout)

        self.workouts.sort(
            key=lambda item: item.scheduled_at,
        )

    # ======================================================

    def extend(
        self,
        workouts: Iterable[PlannedWorkout],
    ):

        for workout in workouts:

            self.add(workout)

    # ======================================================

    def for_day(self, day):

        if isinstance(day, datetime):

            day = day.date()

        return tuple(
            workout
            for workout in self.workouts
            if workout.day == day
        )

    # ======================================================

    def next_workout(
        self,
        reference: datetime | None = None,
    ):

        reference = reference or datetime.now()

        for workout in self.workouts:

            if workout.scheduled_at >= reference:

                return workout

        return None

    # ======================================================

    @property
    def training_days(self):

        return len({
            workout.day
            for workout in self.workouts
            if not workout.is_rest
        })

    # ======================================================

    @property
    def total_duration(self):

        total = timedelta()

        for workout in self.workouts:

            if workout.duration is not None:

                total += workout.duration

        return total

    # ======================================================

    @property
    def total_distance(self):

        return sum(
            workout.distance or 0.0
            for workout in self.workouts
        )

    # ======================================================

    def __len__(self):

        return len(self.workouts)

    # ======================================================

    def __iter__(self):

        return iter(self.workouts)

    # ======================================================

    def __repr__(self):

        return (
            "WeeklyPlan("
            f"{self.start_date} -> {self.end_date}, "
            f"{len(self.workouts)} workouts)"
        )