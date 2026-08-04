"""
PerformanceLab

Complete training-plan presenter.
"""

from collections import defaultdict
from datetime import date, timedelta

from performancelab.training.load import (
    planned_weekly_load,
    planned_workout_load,
)

from .plan_models import (
    CompletePlanData,
    PlanCurrentPhaseData,
    PlanProgressionPointData,
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

    @staticmethod
    def _current_phase_data(
        weeks,
        *,
        reference_day: date,
    ) -> PlanCurrentPhaseData | None:
        """
        Builds the phase containing the reference day.
        """

        current_index = next(
            (
                index
                for index, week
                in enumerate(weeks)
                if (
                    week.start_date
                    <= reference_day
                    <= week.end_date
                )
            ),
            None,
        )

        if current_index is None:
            return None

        current_week = weeks[
            current_index
        ]

        phase_name = (
            current_week.phase
            or "Unassigned"
        )

        phase_start_index = (
            current_index
        )

        while (
            phase_start_index > 0
            and (
                weeks[
                    phase_start_index - 1
                ].phase
                == current_week.phase
            )
        ):
            phase_start_index -= 1

        phase_end_index = (
            current_index
        )

        while (
            phase_end_index
            < len(weeks) - 1
            and (
                weeks[
                    phase_end_index + 1
                ].phase
                == current_week.phase
            )
        ):
            phase_end_index += 1

        return PlanCurrentPhaseData(
            name=phase_name,
            start_date=(
                weeks[
                    phase_start_index
                ].start_date
            ),
            end_date=(
                weeks[
                    phase_end_index
                ].end_date
            ),
            weeks_remaining=(
                phase_end_index
                - current_index
                + 1
            ),
        )


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
        progression = []

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
                    planned_load=(
                        planned_workout_load(
                            workout
                        )
                    ),
                    is_race=(
                        str(
                            workout.intensity
                            or ""
                        ).strip().lower()
                        == "race effort"
                    ),
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
            phase = self.plan.phase_on(
                week_start
            )

            weekly_load = (
                planned_weekly_load(
                    planned_workouts
                )
            )

            duration_minutes = sum(
                (
                    workout.duration
                    .total_seconds()
                    / 60
                )
                for workout
                in planned_workouts
                if workout.duration
                is not None
            )

            distance = sum(
                float(
                    workout.distance
                )
                for workout
                in planned_workouts
                if isinstance(
                    workout.distance,
                    (int, float),
                )
                and not isinstance(
                    workout.distance,
                    bool,
                )
            )

            elevation_gain = sum(
                float(
                    workout.elevation_gain
                )
                for workout
                in planned_workouts
                if isinstance(
                    workout.elevation_gain,
                    (int, float),
                )
                and not isinstance(
                    workout.elevation_gain,
                    bool,
                )
            )

            weeks.append(
                PlanWeekData(
                    start_date=week_start,
                    end_date=(
                        week_start
                        + timedelta(
                            days=6
                        )
                    ),
                    phase=phase,
                    planned_load=(
                        weekly_load
                    ),
                    workouts=(
                        workout_data
                    ),
                )
            )

            progression.append(
                PlanProgressionPointData(
                    week_start=week_start,
                    phase=phase,
                    planned_load=(
                        weekly_load
                    ),
                    duration_minutes=(
                        duration_minutes
                    ),
                    distance=distance,
                    elevation_gain=(
                        elevation_gain
                    ),
                )
            )

        weeks_data = tuple(
            weeks
        )

        return CompletePlanData(
            plan_id=self.plan.plan_id,
            start_date=self.plan.start_date,
            end_date=self.plan.end_date,
            reference_day=reference_day,
            weeks=weeks_data,
            progression=tuple(
                progression
            ),
            current_phase=(
                self._current_phase_data(
                    weeks_data,
                    reference_day=(
                        reference_day
                    ),
                )
            ),
        )