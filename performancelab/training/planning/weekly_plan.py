"""
PerformanceLab

Weekly Plan

Represents one planned training week.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Iterable

from .planned_workout import PlannedWorkout
from .workout_collection import WorkoutCollection


@dataclass
class WeeklyPlan(WorkoutCollection):
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

    def add(
        self,
        workout: PlannedWorkout,
    ):

        if not isinstance(
            workout,
            PlannedWorkout,
        ):

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

    def __repr__(self):

        return (
            "WeeklyPlan("
            f"{self.start_date} -> {self.end_date}, "
            f"{len(self.workouts)} workouts)"
        )