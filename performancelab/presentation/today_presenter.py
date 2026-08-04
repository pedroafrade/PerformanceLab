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
            latest_activity=(
                dashboard.latest_activity
            ),
            latest_activity_summary=(
                latest_activity_summary
            ),
            recovery=recovery,
            training_load=training_load,
            next_event=(
                dashboard.next_event
            ),
        )