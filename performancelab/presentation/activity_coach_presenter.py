"""
PerformanceLab

Training Coach context presenter.
"""

from datetime import (
    date,
    datetime,
    timedelta,
)
from performancelab.coaching.activity_signals import (
    assess_activity_signals,
)
from performancelab.coaching.context import (
    CoachContext,
)
from performancelab.training.load import (
    workout_load,
)

from .activity_coach_models import (
    ActivityCoachAssessmentData,
    ActivityCoachContextData,
    ActivityCoachEventData,
    ActivityCoachFeedbackData,
    ActivityCoachPhysiologyData,
    ActivityCoachPlanData,
    ActivityCoachRecentTrainingData,
    ActivityCoachSensorData,
)
from .activity_models import (
    ActivityListItemData,
)
from .chart import (
    sensor_summary,
)


class ActivityCoachPresenter:
    """
    Builds immutable factual context for one activity.
    """

    def __init__(
        self,
        *,
        activity: ActivityListItemData,
        workout,
        athlete=None,
    ) -> None:

        self.activity = activity
        self.workout = workout
        self.athlete = athlete

    @staticmethod
    def _calendar_day(
        value,
    ) -> date | None:

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        if isinstance(
            value,
            date,
        ):
            return value

        return None

    def _sensor_data(
        self,
        sensor_name: str,
    ) -> ActivityCoachSensorData:

        summary = sensor_summary(
            self.workout,
            sensor_name,
        )

        average = summary[
            "average"
        ]
        maximum = summary[
            "maximum"
        ]

        return ActivityCoachSensorData(
            average=(
                float(average)
                if average is not None
                else None
            ),
            maximum=(
                float(maximum)
                if maximum is not None
                else None
            ),
        )

    def _feedback_data(
        self,
    ) -> ActivityCoachFeedbackData:
        """
        Returns only athlete-recorded subjective feedback.
        """

        feedback = self.workout.feedback

        notes = str(
            feedback.notes
            or ""
        ).strip()

        return ActivityCoachFeedbackData(
            rpe=(
                float(feedback.rpe)
                if feedback.rpe is not None
                else None
            ),
            feeling=(
                float(feedback.feeling)
                if feedback.feeling is not None
                else None
            ),
            sleep_quality=(
                float(feedback.sleep_quality)
                if feedback.sleep_quality is not None
                else None
            ),
            motivation=(
                float(feedback.motivation)
                if feedback.motivation is not None
                else None
            ),
            stress=(
                float(feedback.stress)
                if feedback.stress is not None
                else None
            ),
            muscle_soreness=(
                float(feedback.muscle_soreness)
                if feedback.muscle_soreness is not None
                else None
            ),
            notes=(
                notes
                if notes
                else None
            ),
        )
    
    def _recent_training(
        self,
    ) -> ActivityCoachRecentTrainingData:

        activity_day = self._calendar_day(
            self.activity.workout_date
        )

        if (
            self.athlete is None
            or activity_day is None
        ):
            return (
                ActivityCoachRecentTrainingData()
            )

        start_day = (
            activity_day
            - timedelta(
                days=6
            )
        )

        recent_workouts = []

        for workout in self.athlete.history:

            workout_day = self._calendar_day(
                workout.date
            )

            if (
                workout_day is None
                or workout_day < start_day
                or workout_day > activity_day
            ):
                continue

            recent_workouts.append(
                workout
            )

        total_duration_minutes = sum(
            (
                workout.duration
                .total_seconds()
                / 60
            )
            for workout in recent_workouts
            if workout.duration is not None
        )

        total_load = sum(
            float(
                workout_load(
                    workout
                )
            )
            for workout in recent_workouts
        )

        previous_candidates = [
            workout
            for workout in self.athlete.history
            if (
                self._calendar_day(
                    workout.date
                )
                is not None
                and self._calendar_day(
                    workout.date
                )
                < activity_day
            )
        ]

        previous_workout = (
            max(
                previous_candidates,
                key=lambda workout: (
                    self._calendar_day(
                        workout.date
                    )
                ),
            )
            if previous_candidates
            else None
        )

        previous_title = None
        previous_days_before = None
        previous_load = None

        if previous_workout is not None:

            previous_day = (
                self._calendar_day(
                    previous_workout.date
                )
            )

            previous_title = str(
                previous_workout.info.title
                or previous_workout.sport
                or "Activity"
            )

            previous_days_before = (
                activity_day
                - previous_day
            ).days

            previous_load = float(
                workout_load(
                    previous_workout
                )
            )

        return ActivityCoachRecentTrainingData(
            session_count=len(
                recent_workouts
            ),
            total_duration_minutes=float(
                total_duration_minutes
            ),
            total_load=float(
                total_load
            ),
            previous_title=previous_title,
            previous_days_before=(
                previous_days_before
            ),
            previous_load=previous_load,
        )

    def _is_latest_activity(
        self,
        activity_day: date,
    ) -> bool:

        if self.athlete is None:
            return False

        workout_days = [
            workout_day
            for workout in self.athlete.history
            if (
                workout_day
                := self._calendar_day(
                    workout.date
                )
            )
            is not None
        ]

        if not workout_days:
            return False

        return activity_day == max(
            workout_days
        )

    def _training_context(
        self,
    ) -> tuple[
        ActivityCoachPlanData,
        ActivityCoachEventData,
        ActivityCoachPhysiologyData,
    ]:

        activity_day = self._calendar_day(
            self.activity.workout_date
        )

        if (
            self.athlete is None
            or activity_day is None
        ):
            return (
                ActivityCoachPlanData(),
                ActivityCoachEventData(),
                ActivityCoachPhysiologyData(),
            )

        coach_context = (
            CoachContext.from_athlete(
                self.athlete,
                today=activity_day,
            )
        )

        phase = (
            self.athlete
            .training_plan
            .phase_on(
                activity_day
            )
        )

        plan = ActivityCoachPlanData(
            phase=phase,
        )

        event_entry = (
            coach_context.next_event
        )

        event = getattr(
            event_entry,
            "event",
            None,
        )

        event_data = ActivityCoachEventData()

        if event is not None:

            terrain = str(
                getattr(
                    event,
                    "terrain",
                    "",
                )
                or ""
            ).strip()

            priority = str(
                getattr(
                    event_entry,
                    "priority",
                    "",
                )
                or ""
            ).strip()

            event_data = ActivityCoachEventData(
                name=(
                    str(event.name)
                    if event.name
                    else None
                ),
                sport=(
                    str(event.sport)
                    if event.sport
                    else None
                ),
                distance=(
                    float(event.distance)
                    if event.distance
                    is not None
                    else None
                ),
                elevation_gain=(
                    float(
                        event.elevation_gain
                    )
                    if event.elevation_gain
                    is not None
                    else None
                ),
                terrain=(
                    terrain
                    if terrain
                    else None
                ),
                priority=(
                    priority
                    if priority
                    else None
                ),
                days_until_event=(
                    coach_context
                    .days_until_event
                ),
            )

        state_is_current = (
            self._is_latest_activity(
                activity_day
            )
        )

        training_state = (
            coach_context.training_state
            if state_is_current
            else None
        )

        physiology = (
            ActivityCoachPhysiologyData(
                threshold_hr=(
                    self.athlete
                    .threshold_hr
                ),
                ftp=(
                    float(
                        self.athlete.ftp
                    )
                    if self.athlete.ftp
                    is not None
                    else None
                ),
                state_is_current=(
                    state_is_current
                ),
                readiness=(
                    training_state.readiness
                    if training_state
                    is not None
                    else None
                ),
                recovery_score=(
                    float(
                        training_state
                        .recovery_score
                    )
                    if training_state
                    is not None
                    else None
                ),
                load_state=(
                    training_state.load_state
                    if training_state
                    is not None
                    else None
                ),
            )
        )

        return (
            plan,
            event_data,
            physiology,
        )

    def _build_context(
        self,
    ) -> ActivityCoachContextData:

        environment = (
            self.workout.environment
        )

        terrain = str(
            environment.terrain
            or ""
        ).strip()

        (
            plan,
            event,
            physiology,
        ) = self._training_context()

        return ActivityCoachContextData(
            activity=self.activity,
            heart_rate=self._sensor_data(
                "heart_rate"
            ),
            power=self._sensor_data(
                "power"
            ),
            cadence=self._sensor_data(
                "cadence"
            ),
            temperature=(
                float(
                    environment.temperature
                )
                if environment.temperature
                is not None
                else None
            ),
            humidity=(
                float(
                    environment.humidity
                )
                if environment.humidity
                is not None
                else None
            ),
            terrain=(
                terrain
                if terrain
                else None
            ),
            feedback=(
                self._feedback_data()
            ),
            recent_training=(
                self._recent_training()
            ),
            plan=plan,
            event=event,
            physiology=physiology,
        )


    def build(
        self,
    ) -> ActivityCoachAssessmentData:
        """
        Builds factual context and deterministic domain signals.
        """

        context = self._build_context()

        duration = (
            context.activity.duration
        )

        duration_minutes = (
            duration.total_seconds()
            / 60
            if duration is not None
            else None
        )

        signals = assess_activity_signals(
            planned_load=(
                context.activity.planned_load
            ),
            completed_load=(
                context.activity.completed_load
            ),
            duration_minutes=(
                duration_minutes
            ),
            average_heart_rate=(
                context.heart_rate.average
            ),
            threshold_heart_rate=(
                context.physiology.threshold_hr
            ),
            distance=(
                context.activity.distance
            ),
            elevation_gain=(
                context.activity.elevation_gain
            ),
            event_distance=(
                context.event.distance
            ),
            event_elevation_gain=(
                context.event.elevation_gain
            ),
            readiness=(
                context.physiology.readiness
            ),
            state_is_current=(
                context.physiology.state_is_current
            ),
        )

        return ActivityCoachAssessmentData(
            context=context,
            signals=signals,
        )