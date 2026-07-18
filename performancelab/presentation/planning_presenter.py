"""
PerformanceLab

Planning Presenter

Converts training planning domain objects into dashboard
presentation models.
"""

from datetime import date, datetime, timedelta

from performancelab.presentation.dashboard_models import (
    CoachRecommendationData,
    NextWorkoutData,
    PlanningCardData,
    WeeklyPlanData,
    WeeklyPlanDayData,
)
from performancelab.training.planning import WeeklyPlan


class PlanningPresenter:

    # ======================================================

    def __init__(
        self,
        plan: WeeklyPlan,
        reference: datetime | None = None,
    ):

        if not isinstance(plan, WeeklyPlan):

            raise TypeError(
                "plan must be a WeeklyPlan."
            )

        self.plan = plan
        self.reference = reference or datetime.now()

    # ======================================================

    def _day_status(self, day: date):

        today = self.reference.date()

        if day < today:

            return "past"

        if day == today:

            return "today"

        if self.plan.for_day(day):

            return "planned"

        return "rest"

    # ======================================================

    def _weekly_plan(self):

        days = []

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
                    intensity=(
                        workout.intensity
                        if workout is not None
                        else None
                    ),
                )
            )

        return WeeklyPlanData(
            start_date=self.plan.start_date,
            end_date=self.plan.end_date,
            days=tuple(days),
        )

    # ======================================================

    def _next_workout(self):

        workout = self.plan.next_workout(
            reference=self.reference,
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
            structure=workout.structure,
            equipment=workout.equipment,
        )

    # ======================================================

    def _coach_recommendation(self):

        next_workout = self.plan.next_workout(
            reference=self.reference,
        )

        if next_workout is None:

            return CoachRecommendationData(
                summary="No planned workout is available.",
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
        )

    # ======================================================

    def __repr__(self):

        return (
            "PlanningPresenter("
            f"{self.plan.start_date} -> "
            f"{self.plan.end_date})"
        )