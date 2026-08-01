"""
PerformanceLab

Training Plan Adapter

Applies incremental revisions to future planned workouts.
"""

from datetime import date, datetime

from performancelab.analysis.training_state import (
    TrainingState,
)

from .training_plan import TrainingPlan
from .workout_outcome import (
    WorkoutOutcome,
    WorkoutOutcomeStatus,
)


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

        unsupported_outcome = next(
            (
                outcome
                for outcome in outcomes
                if outcome.status
                in {
                    WorkoutOutcomeStatus.MISSED,
                    WorkoutOutcomeStatus.MODIFIED,
                    WorkoutOutcomeStatus.SUBSTITUTE,
                }
            ),
            None,
        )

        if unsupported_outcome is not None:
            raise NotImplementedError(
                "Adaptive rules are not yet implemented "
                f"for {unsupported_outcome.status.value} "
                "workouts."
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
            workouts=list(
                plan.workouts
            ),
        )