"""
PerformanceLab

Complete training-plan presenter.
"""

from collections import defaultdict
from datetime import date, timedelta

from performancelab.training.load import (
    planned_weekly_load,
)

from .plan_models import (
    CompletePlanData,
    PlanWeekData,
    PlanWorkoutData,
)


class PlanPresenter:
    """
    Organizes a complete TrainingPlan into calendar weeks.
    """

    def __init__(
        self,
        *,
        plan,
        history,
    ) -> None:

        self.plan = plan
        self.history = history

    def _outcomes_by_workout(
        self,
        *,
        reference_day: date,
    ) -> dict[object, str]:
        """
        Indexes outcome status by planned workout.
        """

        return {
            outcome.planned_workout: (
                outcome.status.value
            )
            for outcome in (
                self.plan.assess_outcomes(
                    history=self.history,
                    reference_day=reference_day,
                )
            )
        }

    def build(
        self,
        *,
        reference_day: date,
    ) -> CompletePlanData:
        """
        Builds the complete plan grouped by Monday-first weeks.
        """

        outcomes = (
            self._outcomes_by_workout(
                reference_day=reference_day
            )
        )

        workouts_by_week = defaultdict(
            list
        )

        for workout in self.plan:

            week_start = (
                workout.day
                - timedelta(
                    days=workout.day.weekday()
                )
            )

            workouts_by_week[
                week_start
            ].append(
                workout
            )

        weeks = []

        for week_start in sorted(
            workouts_by_week
        ):

            planned_workouts = tuple(
                sorted(
                    workouts_by_week[
                        week_start
                    ],
                    key=lambda workout: (
                        workout.scheduled_at
                    ),
                )
            )

            workout_data = tuple(
                PlanWorkoutData(
                    scheduled_at=(
                        workout.scheduled_at
                    ),
                    sport=workout.sport,
                    title=(
                        workout.title
                        or "Planned workout"
                    ),
                    duration=workout.duration,
                    distance=workout.distance,
                    elevation_gain=(
                        workout.elevation_gain
                    ),
                    intensity=workout.intensity,
                    phase=workout.phase,
                    status=outcomes.get(
                        workout,
                        "pending",
                    ),
                    prescription_summary=(
                        workout
                        .prescription_summary
                    ),
                    structure=tuple(
                        workout.structure
                    ),
                )
                for workout in planned_workouts
            )

            weeks.append(
                PlanWeekData(
                    start_date=week_start,
                    end_date=(
                        week_start
                        + timedelta(days=6)
                    ),
                    phase=(
                        self.plan.phase_on(
                            week_start
                        )
                    ),
                    planned_load=(
                        planned_weekly_load(
                            planned_workouts
                        )
                    ),
                    workouts=workout_data,
                )
            )

        return CompletePlanData(
            plan_id=self.plan.plan_id,
            start_date=self.plan.start_date,
            end_date=self.plan.end_date,
            reference_day=reference_day,
            weeks=tuple(weeks),
        )