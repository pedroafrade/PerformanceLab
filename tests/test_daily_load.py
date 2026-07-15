"""
PerformanceLab

Tests for Daily Training Load.
"""

from datetime import date, datetime, timedelta

import pytest

from performancelab import History, Workout
from performancelab.training.daily_load import (
    DailyLoad,
    DailyLoadBuilder,
    DailyLoadSeries,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(
    workout_date,
    duration,
    rpe,
):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.duration = duration

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def test_empty_history():

    history = History()

    series = DailyLoadBuilder(history).build()

    assert isinstance(series, DailyLoadSeries)

    assert len(series) == 0

    assert series.dates == []

    assert series.loads == []

    assert series.total_load == 0


# ======================================================

def test_single_workout():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(hours=1),

            5,

        )

    )

    series = DailyLoadBuilder(history).build()

    assert len(series) == 1

    assert series[0] == DailyLoad(

        date=date(2026, 7, 1),

        load=300,

    )


# ======================================================

def test_multiple_workouts_same_day():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(minutes=30),

            4,

        )

    )

    history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(hours=1),

            6,

        )

    )

    series = DailyLoadBuilder(history).build()

    assert len(series) == 1

    assert series.loads == [480]


# ======================================================

def test_rest_days_are_inserted():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 1),

            timedelta(hours=1),

            5,

        )

    )

    history.add(

        create_workout(

            date(2026, 7, 3),

            timedelta(hours=1),

            7,

        )

    )

    series = DailyLoadBuilder(history).build()

    assert series.dates == [

        date(2026, 7, 1),

        date(2026, 7, 2),

        date(2026, 7, 3),

    ]

    assert series.loads == [

        300,

        0.0,

        420,

    ]


# ======================================================

def test_custom_date_range():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 2),

            timedelta(hours=1),

            5,

        )

    )

    series = DailyLoadBuilder(history).build(

        start_date=date(2026, 7, 1),

        end_date=date(2026, 7, 4),

    )

    assert series.loads == [

        0.0,

        300,

        0.0,

        0.0,

    ]


# ======================================================

def test_datetime_is_normalized():

    history = History()

    history.add(

        create_workout(

            datetime(2026, 7, 1, 8, 30),

            timedelta(hours=1),

            5,

        )

    )

    series = DailyLoadBuilder(history).build()

    assert series.dates == [

        date(2026, 7, 1),

    ]


# ======================================================

def test_invalid_workout_is_ignored():

    history = History()

    history.add(

        create_workout(

            date(2026, 7, 1),

            None,

            5,

        )

    )

    series = DailyLoadBuilder(history).build()

    assert len(series) == 0


# ======================================================

def test_invalid_range():

    history = History()

    builder = DailyLoadBuilder(history)

    with pytest.raises(ValueError):

        builder.build(

            start_date=date(2026, 7, 10),

            end_date=date(2026, 7, 1),

        )