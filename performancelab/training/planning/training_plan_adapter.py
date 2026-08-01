"""
PerformanceLab

Training Plan Adapter

Applies incremental revisions to future planned workouts.
"""

from dataclasses import replace
from datetime import date, datetime

from performancelab.analysis.training_state import (
    TrainingState,
)

from .planned_workout import PlannedWorkout
from .training_plan import TrainingPlan
from .workout_outcome import (
    WorkoutOutcome,
    WorkoutOutcomeStatus,
)


OVERLOAD_DURATION_REDUCTION = 0.20
UNDERLOAD_DURATION_INCREASE = 0.05


class TrainingPlanAdapter:
    """
    Adapts a persistent training plan after reconciling it
    with completed training history.
    """

    def adapt(
        self,
        *,
        plan: TrainingPlan,
        outcomes: tuple[WorkoutOutcome, ...],
        training_state: TrainingState,
        reference_day: date,
    ) -> TrainingPlan:
        """
        Returns an incrementally revised training plan.

        Equivalent completed workouts and pending future
        workouts do not require changes.
        """

        self._validate_inputs(
            plan=plan,
            outcomes=outcomes,
            training_state=training_state,
            reference_day=reference_day,
        )

        workouts = list(
            plan.workouts
        )

        has_overload = any(
            (
                outcome.status
                in {
                    WorkoutOutcomeStatus.MODIFIED,
                    WorkoutOutcomeStatus.SUBSTITUTE,
                }
                and outcome.load_difference is not None
                and outcome.load_difference > 0
            )
            for outcome in outcomes
        )

        if (
            has_overload
            and training_state.should_reduce_volume
        ):
            workouts = (
                self._reduce_next_demanding_workout(
                    workouts=workouts,
                    reference_day=reference_day,
                )
            )

        has_underload = any(
            (
                outcome.status
                is WorkoutOutcomeStatus.MISSED
                or (
                    outcome.status
                    in {
                        WorkoutOutcomeStatus.MODIFIED,
                        WorkoutOutcomeStatus.SUBSTITUTE,
                    }
                    and (
                        outcome.load_difference is None
                        or outcome.load_difference < 0
                    )
                )
            )
            for outcome in outcomes
        )

        if (
            has_underload
            and training_state.can_absorb_more_volume
        ):
            workouts = (
                self._increase_next_easy_workout(
                    workouts=workouts,
                    reference_day=reference_day,
                )
            )

        return TrainingPlan(
            plan_id=plan.plan_id,
            start_date=plan.start_date,
            end_date=plan.end_date,
            primary_event_id=(
                plan.primary_event_id
            ),
            competition_event_ids=(
                plan.competition_event_ids
            ),
            workouts=workouts,
        )

    # ======================================================

    @staticmethod
    def _reduce_next_demanding_workout(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
    ) -> list[PlannedWorkout]:
        """
        Reduces the duration of the next unprotected
        demanding workout by 20%.
        """

        updated = list(
            workouts
        )

        candidate_index = next(
            (
                index
                for index, workout
                in enumerate(updated)
                if (
                    workout.day
                    > reference_day
                    and workout.duration is not None
                    and workout.duration.total_seconds()
                    > 0
                    and TrainingPlanAdapter._is_demanding(
                        workout
                    )
                    and not TrainingPlanAdapter._is_protected(
                        workout
                    )
                )
            ),
            None,
        )

        if candidate_index is None:
            return updated

        candidate = updated[
            candidate_index
        ]

        updated[candidate_index] = replace(
            candidate,
            duration=(
                candidate.duration
                * (
                    1.0
                    - OVERLOAD_DURATION_REDUCTION
                )
            ),
        )

        return updated

    # ======================================================

    @staticmethod
    def _increase_next_easy_workout(
        *,
        workouts: list[PlannedWorkout],
        reference_day: date,
    ) -> list[PlannedWorkout]:
        """
        Adds a small fraction of missing load to the next
        unprotected easy workout.

        The missed workout is never moved to another day.
        """

        updated = list(
            workouts
        )

        candidate_index = next(
            (
                index
                for index, workout
                in enumerate(updated)
                if (
                    workout.day
                    > reference_day
                    and workout.duration is not None
                    and workout.duration.total_seconds()
                    > 0
                    and TrainingPlanAdapter._is_easy(
                        workout
                    )
                    and not TrainingPlanAdapter._is_protected(
                        workout
                    )
                )
            ),
            None,
        )

        if candidate_index is None:
            return updated

        candidate = updated[
            candidate_index
        ]

        updated[candidate_index] = replace(
            candidate,
            duration=(
                candidate.duration
                * (
                    1.0
                    + UNDERLOAD_DURATION_INCREASE
                )
            ),
        )

        return updated

    # ======================================================

    @staticmethod
    def _is_easy(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Returns whether a workout can safely receive a
        small duration increase.
        """

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "easy",
                "recovery",
            )
        )

    # ======================================================

    @staticmethod
    def _is_demanding(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Returns whether a workout represents a demanding
        training session.
        """

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "tempo",
                "lt2",
                "threshold",
                "interval",
                "hill",
                "speed",
                "vo2",
            )
        )

    # ======================================================

    @staticmethod
    def _is_protected(
        workout: PlannedWorkout,
    ) -> bool:
        """
        Protects competitions and critical race preparation
        from incremental adaptation.
        """

        phase = str(
            workout.phase or ""
        ).strip().lower()

        if phase in {
            "taper",
            "race",
        }:
            return True

        description = (
            TrainingPlanAdapter._description(
                workout
            )
        )

        return any(
            token in description
            for token in (
                "race",
                "shakeout",
                "pre-race",
                "pre race",
            )
        )

    # ======================================================

    @staticmethod
    def _description(
        workout: PlannedWorkout,
    ) -> str:
        """
        Returns normalized semantic workout information.
        """

        return " ".join(
            str(value or "")
            for value in (
                workout.title,
                workout.intensity,
                workout.objective,
            )
        ).strip().lower()

    # ======================================================

    @staticmethod
    def _validate_inputs(
        *,
        plan: TrainingPlan,
        outcomes: tuple[WorkoutOutcome, ...],
        training_state: TrainingState,
        reference_day: date,
    ) -> None:

        if not isinstance(
            plan,
            TrainingPlan,
        ):
            raise TypeError(
                "plan must be a TrainingPlan."
            )

        if not isinstance(
            outcomes,
            tuple,
        ):
            raise TypeError(
                "outcomes must be a tuple."
            )

        if not all(
            isinstance(
                outcome,
                WorkoutOutcome,
            )
            for outcome in outcomes
        ):
            raise TypeError(
                "outcomes must contain WorkoutOutcome "
                "objects."
            )

        if not isinstance(
            training_state,
            TrainingState,
        ):
            raise TypeError(
                "training_state must be a TrainingState."
            )

        if (
            not isinstance(
                reference_day,
                date,
            )
            or isinstance(
                reference_day,
                datetime,
            )
        ):
            raise TypeError(
                "reference_day must be a date."
            )