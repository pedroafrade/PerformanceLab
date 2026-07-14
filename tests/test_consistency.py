"""
PerformanceLab

Tests for Consistency Analytics.
"""

from datetime import date

from performancelab.analysis.consistency import (
    training_days,
    current_streak,
    longest_streak,
    weekday_distribution,
)

from performancelab.history import History
from performancelab.workout import Workout


# ======================================================

def workout(day):

    w = Workout()

    w.info.date = day

    return w


# ======================================================

def test_training_days():

    history = History()

    history.add(workout(date(2026, 7, 1)))

    history.add(workout(date(2026, 7, 1)))

    history.add(workout(date(2026, 7, 2)))

    assert training_days(history) == 2


# ======================================================

def test_longest_streak():

    history = History()

    history.add(workout(date(2026, 7, 1)))

    history.add(workout(date(2026, 7, 2)))

    history.add(workout(date(2026, 7, 3)))

    history.add(workout(date(2026, 7, 7)))

    assert longest_streak(history) == 3


# ======================================================

def test_current_streak():

    history = History()

    history.add(workout(date(2026, 7, 1)))

    history.add(workout(date(2026, 7, 4)))

    history.add(workout(date(2026, 7, 5)))

    history.add(workout(date(2026, 7, 6)))

    assert current_streak(history) == 3


# ======================================================

def test_weekday_distribution():

    history = History()

    history.add(workout(date(2026, 7, 6)))   # Monday

    history.add(workout(date(2026, 7, 6)))

    history.add(workout(date(2026, 7, 7)))   # Tuesday

    distribution = weekday_distribution(history)

    assert distribution[0] == 2

    assert distribution[1] == 1


# ======================================================

def test_empty_history():

    history = History()

    assert training_days(history) == 0

    assert current_streak(history) == 0

    assert longest_streak(history) == 0

    assert weekday_distribution(history) == {}