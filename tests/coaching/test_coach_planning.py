"""
Tests for the Coach planning façade.

"""

from datetime import date
from unittest.mock import Mock

from performancelab.athlete import Athlete
from performancelab.coaching.coach import Coach
from performancelab.training.planning.planner import Planner
from performancelab.training.planning.weekly_plan import WeeklyPlan


def test_plan_delegates_to_injected_planner():
    athlete = Athlete(
        name="John",
    )

    weekly_plan = Mock(
        spec=WeeklyPlan,
    )

    planner = Mock(
        spec=Planner,
    )
    planner.build.return_value = weekly_plan

    coach = Coach(
        planner=planner,
    )

    result = coach.plan(
        athlete=athlete,
        week_start=date(2026, 7, 20),
        today=date(2026, 7, 23),
    )

    assert result is weekly_plan

    planner.build.assert_called_once_with(
        athlete=athlete,
        week_start=date(2026, 7, 20),
        today=date(2026, 7, 23),
    )