"""
Tests for History.
"""

from performancelab.history import History

from performancelab.workout import Workout


def test_empty_history():

    history = History()

    assert len(history) == 0


def test_add_workout():

    history = History()

    workout = Workout()

    history.add(workout)

    assert len(history) == 1


def test_clear_history():

    history = History()

    history.add(Workout())

    history.clear()

    assert len(history) == 0