"""
PerformanceLab

Planning Presenter

Converts training planning domain objects into dashboard
presentation models.
"""

from datetime import date, datetime, time, timedelta

from performancelab.history import History
from performancelab.presentation.dashboard_models import (
    CoachRecommendationData,
    NextWorkoutData,
    PlanningCardData,
    TrainingPhaseDayData,
    TrainingPhaseTimelineData,
    WeeklyPlanData,
    WeeklyPlanDayData,
)
from performancelab.training.planning import (
    TrainingPlan,
    WeeklyPlan,
)


class PlanningPresenter:

    # ======================================================

    def __init__(
        self,
        plan: WeeklyPlan,
        history: History | None = None,
        reference: datetime | None = None,
        training_plan: TrainingPlan | None = None,
    ):

        if not isinstance(plan, WeeklyPlan):

            raise TypeError(
                "plan must be a WeeklyPlan."
            )

        if history is not None and not isinstance(
            history,
            History,
        ):

            raise TypeError(
                "history must be a History or None."
            )

        if (
            training_plan is not None
            and not isinstance(
                training_plan,
                TrainingPlan,
            )
        ):
            raise TypeError(
                "training_plan must be a "
                "TrainingPlan or None."
            )

        self.plan = plan
        self.history = history
        self.reference = reference or datetime.now()
        self.training_plan = training_plan

    # ======================================================

    @staticmethod
    def _as_date(
        value,
    ) -> date | None:
        """
        Normalize a date or datetime value into a date.
        """

        if value is None:

            return None

        if isinstance(value, datetime):

            return value.date()

        if isinstance(value, date):

            return value

        return None

    # ======================================================

    @staticmethod
    def _workout_value(
        workout,
        *paths: tuple[str, ...],
    ):
        """
        Return the first available nested workout value.
        """

        for path in paths:

            value = workout

            for name in path:

                if value is None:

                    break

                value = getattr(
                    value,
                    name,
                    None,
                )

                if callable(value):

                    value = value()

            if value is not None:

                return value

        return None

    # ======================================================

    def _completed_workouts(self):
        """
        Index completed workouts by calendar day.

        If multiple workouts exist on the same day, the latest
        workout in the history is used for presentation details.
        """

        completed = {}

        if self.history is None:

            return completed

        for workout in self.history:

            workout_date = self._workout_value(
                workout,
                ("info", "date"),
                ("date",),
                ("workout_date",),
            )

            workout_day = self._as_date(
                workout_date
            )

            if workout_day is None:

                continue

            completed[workout_day] = workout

        return completed

    # ======================================================
    def _outcomes_by_day(
        self,
    ) -> dict[date, str]:
        """
        Returns domain-assessed workout outcomes indexed
        by planned calendar day.
        """

        if (
            self.training_plan is None
            or self.history is None
        ):
            return {}

        outcomes = (
            self.training_plan.assess_outcomes(
                history=self.history,
                reference_day=(
                    self.reference.date()
                ),
            )
        )

        return {
            outcome.planned_workout.day: (
                outcome.status.value
            )
            for outcome in outcomes
        }

    # ======================================================

    def _day_status(
        self,
        day: date,
    ) -> str:

        today = self.reference.date()

        if day < today:

            return "past"

        if day == today:

            return "today"

        if self.plan.for_day(day):

            return "planned"

        return "rest"

    # ======================================================
    def _next_uncompleted_workout(self):
        """
        Returns the next planned workout whose calendar
        day does not already contain a completed activity.
        """

        completed_days = set(
            self._completed_workouts()
        )

        reference = (
            self._next_workout_reference()
        )

        workout_source = (
            self.training_plan
            if self.training_plan is not None
            else self.plan
        )

        return next(
            (
                workout
                for workout in workout_source
                if (
                    workout.scheduled_at
                    >= reference
                    and workout.day
                    not in completed_days
                )
            ),
            None,
        )

    # ======================================================

    def _weekly_plan(self):

        days = []

        completed_workouts = (
            self._completed_workouts()
        )

        outcomes_by_day = (
            self._outcomes_by_day()
        )

        next_workout = (
            self._next_uncompleted_workout()
        )

        next_workout_day = None

        if next_workout is not None:

            next_workout_day = self._as_date(
                next_workout.scheduled_at
            )

        today = self.reference.date()

        for offset in range(7):

            day = self.plan.start_date + timedelta(
                days=offset,
            )

            workouts = self.plan.for_day(day)

            workout = (
                workouts[0]
                if workouts
                else None
            )

            completed_workout = (
                completed_workouts.get(day)
            )

            completed_title = None
            completed_sport = None

            if completed_workout is not None:

                completed_title = self._workout_value(
                    completed_workout,
                    ("info", "title"),
                    ("title",),
                )

                completed_sport = self._workout_value(
                    completed_workout,
                    ("info", "sport"),
                    ("sport",),
                )

            days.append(
                WeeklyPlanDayData(
                    day=day,
                    status=self._day_status(day),
                    sport=(
                        workout.sport
                        if workout is not None
                        else None
                    ),
                    title=(
                        workout.title
                        if workout is not None
                        else None
                    ),
                    duration=(
                        workout.duration
                        if workout is not None
                        else None
                    ),
                    distance=(
                        workout.distance
                        if workout is not None
                        else None
                    ),
                    elevation_gain=(
                        workout.elevation_gain
                        if workout is not None
                        else None
                    ),
                    prescription_summary=(
                        workout.prescription_summary
                        if workout is not None
                        else None
                    ),
                    intensity=(
                        workout.intensity
                        if workout is not None
                        else None
                    ),
                    structure=(
                        workout.presentation_structure
                        if workout is not None
                        else ()
                    ),
                    is_today=day == today,
                    is_next_workout=(
                        day == next_workout_day
                    ),
                    completed=(
                        completed_workout
                        is not None
                    ),
                    completed_sport=(
                        str(completed_sport)
                        if completed_sport
                        is not None
                        else None
                    ),
                    completed_title=(
                        str(completed_title)
                        if completed_title
                        is not None
                        else None
                    ),
                    outcome_status=(
                        outcomes_by_day.get(
                            day
                        )
                    ),
                )
            )

        return WeeklyPlanData(
            start_date=self.plan.start_date,
            end_date=self.plan.end_date,
            days=tuple(days),
        )

    # ======================================================

    def _phase_timeline(
        self,
    ) -> TrainingPhaseTimelineData | None:

        training_plan = self.training_plan

        if (
            training_plan is None
            or training_plan.start_date is None
            or training_plan.end_date is None
        ):
            return None

        phase_days = []

        current_day = (
            training_plan.start_date
        )

        while (
            current_day
            <= training_plan.end_date
        ):

            phase_days.append(
                TrainingPhaseDayData(
                    day=current_day,
                    phase=(
                        training_plan.phase_on(
                            current_day
                        )
                    ),
                )
            )

            current_day += timedelta(
                days=1
            )

        return TrainingPhaseTimelineData(
            start_date=(
                training_plan.start_date
            ),
            end_date=(
                training_plan.end_date
            ),
            days=tuple(
                phase_days
            ),
        )

    # ======================================================

    def _next_workout(self):

        workout = (
            self._next_uncompleted_workout()
        )

        if workout is None:

            return None

        return NextWorkoutData(
            scheduled_at=workout.scheduled_at,
            sport=workout.sport,
            title=workout.title,
            duration=workout.duration,
            distance=workout.distance,
            description=workout.description,
            intensity=workout.intensity,
            objective=workout.objective,
            structure=(
                workout.presentation_structure
            ),
            equipment=workout.equipment,
        )

    # ======================================================

    def _coach_recommendation(self):

        next_workout = (
            self._next_uncompleted_workout()
        )

        if next_workout is None:

            return CoachRecommendationData(
                summary=(
                    "No planned workout is available."
                ),
                recommendation=(
                    "Add a workout to the training plan "
                    "to receive a recommendation."
                ),
                status="unavailable",
                warnings=(),
                source="rules",
            )

        title = (
            next_workout.title
            or next_workout.sport
            or "planned session"
        )

        return CoachRecommendationData(
            summary=f"Next session: {title}.",
            recommendation=(
                "Follow the planned session and review "
                "recovery before starting."
            ),
            status="ready",
            warnings=(),
            source="rules",
        )

    # ======================================================

    def build(self):

        return PlanningCardData(
            weekly_plan=self._weekly_plan(),
            next_workout=self._next_workout(),
            coach=self._coach_recommendation(),
            phase_timeline=(
                self._phase_timeline()
            ),
        )

    # ======================================================

    def __repr__(self):

        return (
            "PlanningPresenter("
            f"{self.plan.start_date} -> "
            f"{self.plan.end_date})"
        )
    
    # ======================================================

    def _next_workout_reference(
        self,
    ) -> datetime:
        """
        Includes planned workouts scheduled for the current day.
        """

        return datetime.combine(
            self.reference.date(),
            time.min,
        )
