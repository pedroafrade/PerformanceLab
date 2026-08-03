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
from performancelab.training.planning.planner import (
    WeeklyPlanBuilder,
)

from .dashboard import DashboardData
from .activities_presenter import (
    ActivitiesPresenter,
)
from .planning_presenter import (
    PlanningPresenter,
)
from .today_models import TodayData


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
        return TodayData(
            reference_day=reference_day,
            today_session=today_session,
            next_workout=(
                planning.next_workout
            ),
            coach=planning.coach,
            latest_activity=(
                dashboard.latest_activity
            ),
            latest_activity_summary=(
                latest_activity_summary
            ),
            recovery=(
                dashboard.recovery
            ),
            training_load=(
                dashboard.training_load
            ),
            next_event=(
                dashboard.next_event
            ),
        )