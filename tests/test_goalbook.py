from performancelab.goals import Goal
from performancelab.goals import GoalBook


def test_goalbook_creation():

    goals = GoalBook()

    assert len(goals) == 0


def test_add_goal():

    goals = GoalBook()

    goal = Goal(name="Maratona")

    goals.add(goal)

    assert len(goals) == 1

    assert goals[0] == goal


def test_remove_goal():

    goals = GoalBook()

    goal = Goal(name="Maratona")

    goals.add(goal)

    goals.remove(goal)

    assert len(goals) == 0


def test_clear_goalbook():

    goals = GoalBook()

    goals.add(Goal(name="A"))

    goals.add(Goal(name="B"))

    goals.clear()

    assert len(goals) == 0