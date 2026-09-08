"""
PerformanceLab

Plan Builder Draft

An isolated, non-persistent training-plan workspace.
"""

from dataclasses import dataclass, replace
from datetime import date, datetime

from .planned_workout import PlannedWorkout


@dataclass(frozen=True, slots=True)
class PlanBuilderDraft:
    """
    Editable plan state that remains isolated from the
    athlete's active persistent plan.
    """

    source_plan_id: str
    source_revision_id: str | None

    workouts: tuple[
        PlannedWorkout,
        ...,
    ]

    baseline_workouts: tuple[
        PlannedWorkout,
        ...,
    ]

    @classmethod
    def from_plan(
        cls,
        plan,
    ) -> "PlanBuilderDraft":

        workouts = tuple(
            plan.workouts
        )

        return cls(
            source_plan_id=plan.plan_id,
            source_revision_id=(
                plan.active_revision_id
            ),
            workouts=workouts,
            baseline_workouts=workouts,
        )

    @property
    def has_changes(self) -> bool:

        return (
            self.workouts
            != self.baseline_workouts
        )

    def reset(self) -> "PlanBuilderDraft":

        return replace(
            self,
            workouts=(
                self.baseline_workouts
            ),
        )

    def delete_workout(
        self,
        *,
        workout_day: date,
    ) -> "PlanBuilderDraft":

        self._validate_day(
            workout_day
        )

        revised = tuple(
            workout
            for workout in self.workouts
            if workout.day != workout_day
        )

        if revised == self.workouts:
            raise LookupError(
                "No planned workout exists on that day."
            )

        return replace(
            self,
            workouts=revised,
        )

    def add_workout(
        self,
        *,
        template: PlannedWorkout,
        workout_day: date,
    ) -> "PlanBuilderDraft":

        if not isinstance(
            template,
            PlannedWorkout,
        ):
            raise TypeError(
                "template must be a PlannedWorkout."
            )

        self._validate_day(
            workout_day
        )

        if any(
            workout.day == workout_day
            for workout in self.workouts
        ):
            raise ValueError(
                "The target day already contains a workout."
            )

        scheduled_at = datetime.combine(
            workout_day,
            template.scheduled_at.time(),
        )

        added = replace(
            template,
            scheduled_at=scheduled_at,
        )

        return replace(
            self,
            workouts=tuple(
                sorted(
                    (
                        *self.workouts,
                        added,
                    ),
                    key=lambda workout: (
                        workout.scheduled_at
                    ),
                )
            ),
        )

    def move_workout(
        self,
        *,
        source_day: date,
        target_day: date,
    ) -> "PlanBuilderDraft":
        """
        Moves a workout to an empty day or swaps two
        existing workouts.
        """

        self._validate_day(
            source_day
        )

        self._validate_day(
            target_day
        )

        if source_day == target_day:
            return self

        source = self._workout_on(
            source_day
        )

        if source is None:
            raise LookupError(
                "No planned workout exists on the source day."
            )

        target = self._workout_on(
            target_day
        )

        revised = []

        for workout in self.workouts:

            if workout is source:

                revised.append(
                    replace(
                        workout,
                        scheduled_at=(
                            datetime.combine(
                                target_day,
                                workout
                                .scheduled_at
                                .time(),
                            )
                        ),
                    )
                )

                continue

            if (
                target is not None
                and workout is target
            ):

                revised.append(
                    replace(
                        workout,
                        scheduled_at=(
                            datetime.combine(
                                source_day,
                                workout
                                .scheduled_at
                                .time(),
                            )
                        ),
                    )
                )

                continue

            revised.append(
                workout
            )

        return replace(
            self,
            workouts=tuple(
                sorted(
                    revised,
                    key=lambda workout: (
                        workout.scheduled_at
                    ),
                )
            ),
        )

    def _workout_on(
        self,
        workout_day: date,
    ) -> PlannedWorkout | None:

        return next(
            (
                workout
                for workout in self.workouts
                if workout.day == workout_day
            ),
            None,
        )

    @staticmethod
    def _validate_day(
        value,
    ) -> None:

        if (
            not isinstance(value, date)
            or isinstance(value, datetime)
        ):
            raise TypeError(
                "workout day must be a date."
            )