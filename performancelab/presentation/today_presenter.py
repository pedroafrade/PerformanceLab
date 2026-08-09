"""
PerformanceLab

Today presenter.
"""

from datetime import (
    date,
    datetime,
    time,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.coaching import (
    build_daily_training_guidance,
)
from performancelab.training.planning import (
    TrainingPlanAdaptation,
    WorkoutOutcomeStatus,
)
from performancelab.training.planning.planner import (
    WeeklyPlanBuilder,
)

from .activities_presenter import (
    ActivitiesPresenter,
)
from .dashboard import DashboardData
from .planning_presenter import (
    PlanningPresenter,
)
from .today_models import (
    TodayAdaptationData,
    TodayData,
    TodayGuidanceData,
    TodayReadinessData,
)


class TodayPresenter:
    """
    Builds the daily athlete context used by the
    Today page.
    """

    def __init__(
        self,
        athlete: Athlete,
    ) -> None:

        self.athlete = athlete

    def build(
        self,
        *,
        reference_day: date | None = None,
    ) -> TodayData:

        reference_day = (
            reference_day
            or date.today()
        )

        dashboard = DashboardData(
            self.athlete
        )

        weekly_plan = (
            WeeklyPlanBuilder(
                self.athlete.training_plan
            ).week(
                reference_day
            )
        )

        planning = PlanningPresenter(
            plan=weekly_plan,
            history=self.athlete.history,
            reference=datetime.combine(
                reference_day,
                time.min,
            ),
            training_plan=(
                self.athlete.training_plan
            ),
        ).build()

        today_session = next(
            (
                day
                for day
                in planning.weekly_plan.days
                if day.day
                == reference_day
            ),
            None,
        )

        planned_workout = next(
            (
                workout
                for workout
                in self.athlete.training_plan
                .for_day(reference_day)
                if not workout.is_rest
            ),
            None,
        )

        activities = ActivitiesPresenter(
            self.athlete.history,
            training_plan=(
                self.athlete.training_plan
            ),
            reference_day=(
                reference_day
            ),
        ).build()

        latest_activity_summary = (
            activities[0]
            if activities
            else None
        )

        today_activity_summary = next(
            (
                activity
                for activity in activities
                if (
                    (
                        activity.workout_date.date()
                        if isinstance(
                            activity.workout_date,
                            datetime,
                        )
                        else activity.workout_date
                    )
                    == reference_day
                )
            ),
            None,
        )

        recovery = dashboard.recovery
        training_load = (
            dashboard.training_load
        )
        training_state = (
            self.athlete.analytics
            .training_state
        )
        domain_guidance = (
            build_daily_training_guidance(
                training_state=training_state,
                workout=planned_workout,
            )
        )

        latest_adaptation = (
            self.athlete.training_plan
            .adaptations[-1]
            if self.athlete.training_plan
            .adaptations
            else None
        )

        return TodayData(
            reference_day=reference_day,
            today_session=today_session,
            next_workout=(
                planning.next_workout
            ),
            coach=planning.coach,
            readiness=TodayReadinessData(
                recovery_score=(
                    recovery.score
                ),
                recovery_status=(
                    recovery.status
                ),
                form=training_state.form,
                recent_load=(
                    training_load.acute_load
                ),
            ),
            guidance=TodayGuidanceData(
                reasons=(
                    domain_guidance.reasons
                ),
                cautions=(
                    domain_guidance.cautions
                ),
            ),
            latest_adaptation=(
                self._adaptation_data(
                    latest_adaptation
                )
                if latest_adaptation
                is not None
                else None
            ),
            latest_activity=(
                dashboard.latest_activity
            ),
            latest_activity_summary=(
                latest_activity_summary
            ),
            today_activity_summary=(
                today_activity_summary
            ),
            recovery=recovery,
            training_load=training_load,
            next_event=(
                dashboard.next_event
            ),
        )

    @staticmethod
    def _adaptation_prescription(
        workout,
    ) -> str | None:
        """
        Returns the most useful concise execution dose
        available for one planned workout.
        """

        if workout is None:
            return None

        interval_step = next(
            (
                str(step).strip()
                for step in getattr(
                    workout,
                    "structure",
                    (),
                )
                if (
                    str(step).strip()
                    and "×" in str(step)
                )
            ),
            None,
        )

        if interval_step:
            return interval_step

        prescription_summary = str(
            getattr(
                workout,
                "prescription_summary",
                "",
            )
            or ""
        ).strip()

        return (
            prescription_summary
            or None
        )


    def _adapted_workout(
        self,
        adaptation: TrainingPlanAdaptation,
    ):
        """
        Finds the current planned workout represented by
        an adaptation.
        """

        return next(
            (
                workout
                for workout
                in self.athlete.training_plan
                if (
                    workout.day
                    == adaptation.workout_day
                    and (
                        workout.title
                        or ""
                    )
                    == adaptation.workout_title
                )
            ),
            None,
        )


    def _adaptation_data(
        self,
        adaptation: TrainingPlanAdaptation,
    ) -> TodayAdaptationData:
        """
        Converts a domain adaptation into concise UI data.

        Older adaptations recover their revised execution
        dose from the current planned workout.
        """

        adapted_workout = (
            self._adapted_workout(
                adaptation
            )
        )

        revised_prescription = (
            adaptation.revised_prescription
            or self._adaptation_prescription(
                adapted_workout
            )
        )

        return TodayAdaptationData(
            workout_title=(
                adaptation.workout_title
            ),
            previous_minutes=round(
                adaptation.previous_duration
                .total_seconds()
                / 60
            ),
            revised_minutes=round(
                adaptation.revised_duration
                .total_seconds()
                / 60
            ),
            reason=(
                TodayPresenter
                ._adaptation_reason(
                    adaptation
                )
            ),
            previous_distance=(
                adaptation.previous_distance
            ),
            revised_distance=(
                adaptation.revised_distance
            ),
            previous_elevation_gain=(
                adaptation.previous_elevation_gain
            ),
            revised_elevation_gain=(
                adaptation.revised_elevation_gain
            ),
            previous_prescription=(
                adaptation.previous_prescription
            ),
            revised_prescription=(
                revised_prescription
            ),
        )

    @staticmethod
    def _adaptation_reason(
        adaptation: TrainingPlanAdaptation,
    ) -> str:
        """
        Explains which reconciled outcome changed the plan.
        """

        if (
            adaptation.load_difference
            is not None
            and adaptation.load_difference > 0
        ):
            return (
                "Completed load was higher than planned."
            )

        if (
            adaptation.load_difference
            is not None
            and adaptation.load_difference < 0
        ):
            return (
                "Completed load was lower than planned."
            )

        if (
            adaptation.trigger_status
            is WorkoutOutcomeStatus.MISSED
        ):
            return (
                "A missed session changed future training."
            )

        return (
            "A completed session changed future training."
        )
