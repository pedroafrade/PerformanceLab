"""
PerformanceLab

Training Plan Reconciler

Reconciles a persistent training plan with completed
training history exactly once for each closed period.
"""

from datetime import date, datetime, timedelta

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.history import History

from .training_plan import TrainingPlan
from .training_plan_adapter import (
    TrainingPlanAdapter,
)


class TrainingPlanReconciler:
    """
    Coordinates outcome assessment and incremental
    training-plan adaptation.
    """

    def __init__(
        self,
        adapter: TrainingPlanAdapter | None = None,
    ) -> None:

        self.adapter = (
            adapter or TrainingPlanAdapter()
        )

    # ======================================================

    def reconcile(
        self,
        *,
        plan: TrainingPlan,
        history: History,
        training_state: TrainingState,
        through_day: date,
    ) -> TrainingPlan:
        """
        Reconciles all unprocessed planned workouts up to
        and including through_day.
        """

        self._validate_inputs(
            plan=plan,
            history=history,
            training_state=training_state,
            through_day=through_day,
        )

        if (
            plan.reconciled_through is not None
            and through_day
            <= plan.reconciled_through
        ):
            return plan

        previous_boundary = (
            plan.reconciled_through
        )

        assessment_reference_day = (
            through_day
            + timedelta(days=1)
        )

        outcomes = tuple(
            outcome
            for outcome in plan.assess_outcomes(
                history=history,
                reference_day=(
                    assessment_reference_day
                ),
            )
            if (
                outcome.planned_workout.day
                <= through_day
                and (
                    previous_boundary is None
                    or outcome.planned_workout.day
                    > previous_boundary
                )
            )
        )

        adapted = self.adapter.adapt(
            plan=plan,
            outcomes=outcomes,
            training_state=training_state,
            reference_day=through_day,
        )

        adapted.reconciled_through = (
            through_day
        )

        reconciled_workout_ids = list(
            adapted.reconciled_workout_ids
        )

        known_workout_ids = set(
            reconciled_workout_ids
        )

        for workout in history:

            workout_day = self._workout_day(
                workout
            )

            if workout_day is None:
                continue

            if workout_day > through_day:
                continue

            if (
                adapted.start_date is not None
                and workout_day
                < adapted.start_date
            ):
                continue

            if (
                adapted.end_date is not None
                and workout_day
                > adapted.end_date
            ):
                continue

            if (
                workout.workout_id
                in known_workout_ids
            ):
                continue

            reconciled_workout_ids.append(
                workout.workout_id
            )

            known_workout_ids.add(
                workout.workout_id
            )

        adapted.reconciled_workout_ids = tuple(
            reconciled_workout_ids
        )

        return adapted

    # ======================================================
    def reconcile_closed_days(
        self,
        *,
        plan: TrainingPlan,
        history: History,
        training_state: TrainingState,
        today: date | None = None,
    ) -> TrainingPlan:
        """
        Reconciles completed calendar days when the
        application loads.

        The current day remains open because its planned
        workout may still be completed later.
        """

        reference_day = (
            today or date.today()
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
                "today must be a date or None."
            )

        return self.reconcile(
            plan=plan,
            history=history,
            training_state=training_state,
            through_day=(
                reference_day
                - timedelta(days=1)
            ),
        )

    # ======================================================
    
    @staticmethod
    def _workout_day(
        workout,
    ) -> date | None:
        """
        Returns the workout calendar day when available.
        """

        workout_day = workout.date

        if isinstance(
            workout_day,
            datetime,
        ):
            workout_day = (
                workout_day.date()
            )

        if not isinstance(
            workout_day,
            date,
        ):
            return None

        return workout_day

    # ======================================================

    @staticmethod
    def _validate_inputs(
        *,
        plan: TrainingPlan,
        history: History,
        training_state: TrainingState,
        through_day: date,
    ) -> None:

        if not isinstance(
            plan,
            TrainingPlan,
        ):
            raise TypeError(
                "plan must be a TrainingPlan."
            )

        if not isinstance(
            history,
            History,
        ):
            raise TypeError(
                "history must be a History."
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
                through_day,
                date,
            )
            or isinstance(
                through_day,
                datetime,
            )
        ):
            raise TypeError(
                "through_day must be a date."
            )

    # ======================================================

    def __repr__(self) -> str:

        return (
            "TrainingPlanReconciler("
            f"adapter={self.adapter!r})"
        )