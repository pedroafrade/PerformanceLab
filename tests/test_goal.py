"""
Tests for Goal.
"""

from performancelab.goals import Goal


def test_goal_creation():

    goal = Goal(

        name="Trail Serra da Estrela",

        priority="A"

    )

    assert goal.name == "Trail Serra da Estrela"

    assert goal.priority == "A"


def test_goal_without_date():

    goal = Goal()

    assert goal.is_future is False

    assert goal.days_remaining is None