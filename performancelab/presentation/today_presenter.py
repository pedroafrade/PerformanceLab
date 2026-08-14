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
    DailyTrainingDecision,
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
    TodaySessionCardData,
    TodayTemporaryAdjustmentData,
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
        reference_time: (
            datetime | None
        ) = None,
    ) -> TodayData:

        if (
            reference_time is not None
            and reference_day is not None
            and reference_time.date()
            != reference_day
        ):
            raise ValueError(
                "reference_time must belong "
                "to reference_day"
            )

        reference_day = (
            reference_day
            or (
                reference_time.date()
                if reference_time
                is not None
                else date.today()
            )
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
            .training_state_at(
                reference_time=(
                    reference_time
                )
            )
            if reference_time
            is not None
            else self.athlete.analytics
            .training_state
        )
        domain_guidance = (
            build_daily_training_guidance(
                training_state=training_state,
                workout=planned_workout,
                workout_completed=(
                    today_activity_summary
                    is not None
                ),
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
            session_card=(
                self._session_card_data(
                    today_session=(
                        today_session
                    ),
                    next_workout=(
                        planning.next_workout
                    ),
                )
            ),
            coach=planning.coach,
            readiness=TodayReadinessData(
                recovery_score=(
                    training_state
                    .recovery_score
                ),
                recovery_balance=(
                    training_state
                    .recovery_balance
                ),
                recovery_status=(
                    training_state
                    .recovery_status
                ),
                form=training_state.form,
                recent_load=(
                    training_load.acute_load
                ),
                reference_time=(
                    training_state
                    .reference_time
                ),
                hours_since_last_workout=(
                    training_state
                    .hours_since_last_workout
                ),
                recovery_is_time_aware=(
                    training_state
                    .recovery_is_time_aware
                ),
            ),
            guidance=TodayGuidanceData(
                decision=(
                    domain_guidance
                    .decision
                    .value
                ),
                title=(
                    self._decision_title(
                        domain_guidance
                        .decision
                    )
                ),
                action=(
                    self._decision_action(
                        domain_guidance
                        .decision
                    )
                ),
                plan_is_modified=False,
                temporary_adjustment=(
                    self._temporary_adjustment_data(
                        domain_guidance
                        .temporary_adjustment
                    )
                ),
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
    def _session_duration_label(
        duration,
    ) -> str | None:
        """
        Formats a planned session duration.
        """

        if duration is None:
            return None

        total_minutes = round(
            duration.total_seconds()
            / 60
        )

        hours, minutes = divmod(
            total_minutes,
            60,
        )

        if hours and minutes:
            return (
                f"{hours}h {minutes:02d}m"
            )

        if hours:
            return f"{hours}h"

        return f"{minutes} min"

    @classmethod
    def _session_card_data(
        cls,
        *,
        today_session,
        next_workout,
    ) -> TodaySessionCardData:
        """
        Selects the session presented on the Today page.

        Today's planned session takes priority. On a rest
        day, the next future planned session is previewed.
        """

        if (
            today_session is not None
            and today_session.title
        ):
            metadata = tuple(
                value
                for value in (
                    today_session.sport,
                    cls._session_duration_label(
                        today_session.duration
                    ),
                    today_session.intensity,
                )
                if value
            )

            status = (
                today_session.outcome_status
                .replace("_", " ")
                .title()
                if (
                    today_session
                    .outcome_status
                )
                else "Planned"
            )

            return TodaySessionCardData(
                heading="Today's session",
                title=today_session.title,
                metadata=(
                    " · ".join(metadata)
                    or "Planned training session"
                ),
                status=status,
                structure=tuple(
                    today_session.structure
                ),
            )

        if next_workout is not None:
            scheduled_at = (
                next_workout.scheduled_at
            )

            scheduled_label = (
                (
                    f"{scheduled_at:%A}, "
                    f"{scheduled_at.day} "
                    f"{scheduled_at:%B}"
                )
                if scheduled_at
                is not None
                else None
            )

            metadata = tuple(
                value
                for value in (
                    scheduled_label,
                    next_workout.sport,
                    cls._session_duration_label(
                        next_workout.duration
                    ),
                    next_workout.intensity,
                )
                if value
            )

            return TodaySessionCardData(
                heading="Next Session",
                title=(
                    next_workout.title
                    or "Planned session"
                ),
                metadata=(
                    " · ".join(metadata)
                    or "Next planned training session"
                ),
                status="Planned",
                structure=tuple(
                    next_workout.structure
                ),
            )

        return TodaySessionCardData(
            heading="Today's session",
            title="Rest day",
            metadata=(
                "No future training is currently planned."
            ),
            status="Recovery",
            structure=(),
        )

    @staticmethod
    def _temporary_adjustment_data(
        adjustment,
    ) -> (
        TodayTemporaryAdjustmentData
        | None
    ):
        """
        Converts the domain adjustment into immutable
        presentation data.
        """

        if adjustment is None:
            return None

        maximum_minutes = round(
            adjustment.maximum_duration
            .total_seconds()
            / 60
        )

        return TodayTemporaryAdjustmentData(
            title=adjustment.title,
            intensity=adjustment.intensity,
            maximum_minutes=maximum_minutes,
            replaces_planned_session=(
                adjustment
                .replaces_planned_session
            ),
            explanation=(
                adjustment.explanation
            ),
        )

    @staticmethod
    def _decision_title(
        decision: DailyTrainingDecision,
    ) -> str:
        """
        Returns a concise athlete-facing daily decision.
        """

        titles = {
            DailyTrainingDecision.COMPLETED: (
                "Today's training is complete"
            ),
            DailyTrainingDecision.PROCEED: (
                "Follow the planned session"
            ),
            DailyTrainingDecision.REDUCE_VOLUME: (
                "Shorten today's planned session"
            ),
            DailyTrainingDecision.EASY_ONLY: (
                "Train easy today"
            ),
            (
                DailyTrainingDecision
                .RECOVERY_AS_PLANNED
            ): (
                "Follow the recovery session"
            ),
            DailyTrainingDecision.RECOVERY_ONLY: (
                "Prioritise recovery today"
            ),
            DailyTrainingDecision.REST: (
                "Rest and recover today"
            ),
            DailyTrainingDecision.REVIEW_REQUIRED: (
                "Review readiness before starting"
            ),
        }

        return titles[
            decision
        ]

    @staticmethod
    def _decision_action(
        decision: DailyTrainingDecision,
    ) -> str:
        """
        Explains what the athlete should do today.
        """

        actions = {
            DailyTrainingDecision.COMPLETED: (
                "The completed activity is today's "
                "training stimulus. Use the remaining "
                "day for recovery."
            ),
            DailyTrainingDecision.PROCEED: (
                "Complete the planned session within "
                "its prescribed duration and intensity."
            ),
            DailyTrainingDecision.REDUCE_VOLUME: (
                "Keep the planned type of training, "
                "but reduce its duration and do not "
                "add distance, elevation or repetitions."
            ),
            DailyTrainingDecision.EASY_ONLY: (
                "Replace the planned intensity with "
                "a shorter easy session."
            ),
            (
                DailyTrainingDecision
                .RECOVERY_AS_PLANNED
            ): (
                "Complete the planned recovery session "
                "only if it feels appropriate. Rest "
                "remains a valid option."
            ),
            DailyTrainingDecision.RECOVERY_ONLY: (
                "Do not perform the planned training "
                "stimulus. Choose rest or very light "
                "recovery work according to how you feel."
            ),
            DailyTrainingDecision.REST: (
                "No training stimulus is recommended "
                "today."
            ),
            DailyTrainingDecision.REVIEW_REQUIRED: (
                "Review symptoms, subjective readiness "
                "and race priority before deciding "
                "whether to start."
            ),
        }

        return actions[
            decision
        ]

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
