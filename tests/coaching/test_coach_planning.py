"""
Tests for the Coach planning façade.

"""

from datetime import date
from unittest.mock import Mock

from performancelab.athlete import Athlete
from performancelab.coaching.coach import Coach
from performancelab.training.planning.planner import Planner
from performancelab.training.planning.weekly_plan import WeeklyPlan
from performancelab.training.planning.training_plan import (
    TrainingPlan,
)


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

def test_complete_training_plan_delegates_to_planner():

    athlete = Athlete(
        name="John",
    )

    training_plan = Mock(
        spec=TrainingPlan,
    )

    planner = Mock(
        spec=Planner,
    )

    planner.build_training_plan.return_value = (
        training_plan
    )

    coach = Coach(
        planner=planner,
    )

    result = coach.build_training_plan(
        athlete=athlete,
        today=date(
            2026,
            7,
            29,
        ),
    )

    assert result is training_plan

    planner.build_training_plan.assert_called_once_with(
        athlete=athlete,
        today=date(
            2026,
            7,
            29,
        ),
    )