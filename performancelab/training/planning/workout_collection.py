"""
PerformanceLab

Workout Collection

Common behaviour shared by collections of planned workouts.
"""

from datetime import datetime, timedelta

from .planned_workout import PlannedWorkout


class WorkoutCollection:
    """
    Shared behaviour for collections of planned workouts.
    """

    workouts: list[PlannedWorkout]

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
    ) -> PlannedWorkout | None:

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