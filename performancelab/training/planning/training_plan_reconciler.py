"""
PerformanceLab

Training Plan Reconciler

Reconciles a persistent training plan with completed
training history exactly once for each closed period.
"""

from dataclasses import replace
from datetime import date, datetime, timedelta

from performancelab.analysis.training_state import (
    TrainingState,
)
from performancelab.history import History

from .training_plan import TrainingPlan
from .training_plan_adapter import (
    TrainingPlanAdapter,
)
from .workout_outcome import (
    assess_workout_outcome,
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
        Reconciles new plan days and completed workouts
        that have not previously been processed.
        """

        self._validate_inputs(
            plan=plan,
            history=history,
            training_state=training_state,
            through_day=through_day,
        )

        previous_boundary = (
            plan.reconciled_through
        )

        is_closed_period = (
            previous_boundary is not None
            and through_day
            <= previous_boundary
        )

        if (
            is_closed_period
            and not plan.reconciled_workout_ids
        ):

            reconciled_workout_ids = (
                self._collect_workout_ids(
                    plan=plan,
                    history=history,
                    through_day=(
                        previous_boundary
                    ),
                )
            )

            if not reconciled_workout_ids:
                return plan

            return replace(
                plan,
                reconciled_workout_ids=(
                    reconciled_workout_ids
                ),
                workouts=list(
                    plan.workouts
                ),
            )

        new_workout_ids = (
            self._unreconciled_workout_ids(
                plan=plan,
                history=history,
                through_day=through_day,
            )
        )

        has_new_period = (
            previous_boundary is None
            or through_day
            > previous_boundary
        )

        if (
            not has_new_period
            and not new_workout_ids
        ):
            return plan

        assessment_reference_day = (
            through_day
            + timedelta(days=1)
        )

        period_outcomes = tuple(
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

        late_outcomes = (
            self._assess_late_workouts(
                plan=plan,
                history=history,
                new_workout_ids=(
                    new_workout_ids
                ),
                previous_boundary=(
                    previous_boundary
                ),
                reference_day=(
                    assessment_reference_day
                ),
            )
        )

        outcomes = (
            period_outcomes
            + late_outcomes
        )

        adaptation_reference_day = (
            through_day
        )

        if (
            previous_boundary is not None
            and previous_boundary
            > adaptation_reference_day
        ):
            adaptation_reference_day = (
                previous_boundary
            )

        adapted = self.adapter.adapt(
            plan=plan,
            outcomes=outcomes,
            training_state=training_state,
            reference_day=(
                adaptation_reference_day
            ),
        )

        if (
            previous_boundary is None
            or through_day
            > previous_boundary
        ):
            adapted.reconciled_through = (
                through_day
            )

        else:
            adapted.reconciled_through = (
                previous_boundary
            )

        adapted.reconciled_workout_ids = (
            self._collect_workout_ids(
                plan=adapted,
                history=history,
                through_day=(
                    adapted.reconciled_through
                ),
            )
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
    @classmethod
    def _assess_late_workouts(
        cls,
        *,
        plan: TrainingPlan,
        history: History,
        new_workout_ids: tuple[str, ...],
        previous_boundary: date | None,
        reference_day: date,
    ):
        """
        Assesses each new workout imported into an already
        reconciled calendar day.
        """

        if (
            previous_boundary is None
            or not new_workout_ids
        ):
            return ()

        new_workout_id_set = set(
            new_workout_ids
        )

        planned_by_day = {
            workout.day: workout
            for workout in plan.workouts
        }

        outcomes = []

        for workout in history:

            if (
                workout.workout_id
                not in new_workout_id_set
            ):
                continue

            workout_day = cls._workout_day(
                workout
            )

            if (
                workout_day is None
                or workout_day
                > previous_boundary
            ):
                continue

            planned_workout = (
                planned_by_day.get(
                    workout_day
                )
            )

            if planned_workout is None:
                continue

            outcomes.append(
                assess_workout_outcome(
                    planned_workout=(
                        planned_workout
                    ),
                    completed_workout=workout,
                    reference_day=(
                        reference_day
                    ),
                )
            )

        return tuple(outcomes)

    # ======================================================
    
    @classmethod
    def _unreconciled_workout_ids(
        cls,
        *,
        plan: TrainingPlan,
        history: History,
        through_day: date,
    ) -> tuple[str, ...]:
        """
        Returns workout identities inside the closed plan
        horizon that have not previously been processed.
        """

        known_workout_ids = set(
            plan.reconciled_workout_ids
        )

        return tuple(
            workout_id
            for workout_id
            in cls._collect_workout_ids(
                plan=plan,
                history=history,
                through_day=through_day,
            )
            if workout_id
            not in known_workout_ids
        )

    # ======================================================
    
    @classmethod
    def _collect_workout_ids(
        cls,
        *,
        plan: TrainingPlan,
        history: History,
        through_day: date,
    ) -> tuple[str, ...]:
        """
        Collects workout identities inside the closed
        training-plan horizon without duplicates.
        """

        reconciled_workout_ids = list(
            plan.reconciled_workout_ids
        )

        known_workout_ids = set(
            reconciled_workout_ids
        )

        for workout in history:

            workout_day = cls._workout_day(
                workout
            )

            if workout_day is None:
                continue

            if workout_day > through_day:
                continue

            if (
                plan.start_date is not None
                and workout_day
                < plan.start_date
            ):
                continue

            if (
                plan.end_date is not None
                and workout_day
                > plan.end_date
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

        return tuple(
            reconciled_workout_ids
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