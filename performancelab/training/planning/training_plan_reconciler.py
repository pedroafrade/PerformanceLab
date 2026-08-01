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

        return adapted

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