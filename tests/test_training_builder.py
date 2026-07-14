"""
PerformanceLab

Tests for WeeklyBuilder.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.history import History
from performancelab.training import WeeklyBuilder


# ======================================================
# Helpers
# ======================================================

def create_workout(workout_date, sport="Running"):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.sport = sport
    workout.info.distance = 10
    workout.info.duration = timedelta(hours=1)

    return workout


# ======================================================
# Tests
# ======================================================

def test_empty_history():

    builder = WeeklyBuilder(History())

    assert builder.build() == []


# ======================================================

def test_week_start():

    monday = WeeklyBuilder.week_start(

        date(2026, 7, 8)

    )

    assert monday == date(2026, 7, 6)


# ======================================================

def test_week_end():

    sunday = WeeklyBuilder.week_end(

        date(2026, 7, 8)

    )

    assert sunday == date(2026, 7, 12)


# ======================================================

def test_build_single_week():

    history = History()

    history.add(create_workout(date(2026, 7, 6)))
    history.add(create_workout(date(2026, 7, 8)))
    history.add(create_workout(date(2026, 7, 12)))

    builder = WeeklyBuilder(history)

    weeks = builder.build()

    assert len(weeks) == 1
    assert weeks[0].workouts == 3


# ======================================================

def test_build_multiple_weeks():

    history = History()

    history.add(create_workout(date(2026, 7, 6)))
    history.add(create_workout(date(2026, 7, 15)))
    history.add(create_workout(date(2026, 7, 25)))

    builder = WeeklyBuilder(history)

    weeks = builder.build()

    assert len(weeks) == 3


# ======================================================

def test_specific_week():

    history = History()

    history.add(create_workout(date(2026, 7, 7)))
    history.add(create_workout(date(2026, 7, 8)))
    history.add(create_workout(date(2026, 7, 18)))

    builder = WeeklyBuilder(history)

    week = builder.week(date(2026, 7, 9))

    assert week.workouts == 2
    assert week.start_date == date(2026, 7, 6)
    assert week.end_date == date(2026, 7, 12)


# ======================================================

def test_builder_repr():

    history = History()

    history.add(create_workout(date(2026, 7, 7)))

    builder = WeeklyBuilder(history)

    assert "WeeklyBuilder" in repr(builder)