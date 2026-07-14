"""
PerformanceLab

Tests for MonthlyBuilder.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import (
    WeeklySummary,
    MonthlyBuilder,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(workout_date):

    workout = Workout()

    workout.info.date = workout_date
    workout.info.sport = "Running"
    workout.info.distance = 10
    workout.info.duration = timedelta(hours=1)

    return workout


def create_week(start_date):

    week = WeeklySummary(

        start_date=start_date,

        end_date=start_date + timedelta(days=6),

    )

    week.history.add(

        create_workout(start_date)

    )

    return week


# ======================================================
# Tests
# ======================================================

def test_empty_builder():

    builder = MonthlyBuilder([])

    assert builder.build() == []


# ======================================================

def test_single_month():

    weeks = [

        create_week(date(2026, 7, 6)),

        create_week(date(2026, 7, 13)),

        create_week(date(2026, 7, 20)),

    ]

    builder = MonthlyBuilder(weeks)

    months = builder.build()

    assert len(months) == 1

    assert months[0].year == 2026
    assert months[0].month == 7

    assert len(months[0].weeks) == 3


# ======================================================

def test_multiple_months():

    weeks = [

        create_week(date(2026, 6, 29)),   # June

        create_week(date(2026, 7, 6)),    # July

        create_week(date(2026, 8, 3)),    # August

    ]

    builder = MonthlyBuilder(weeks)

    months = builder.build()

    assert len(months) == 3


# ======================================================

def test_month_lookup():

    weeks = [

        create_week(date(2026, 7, 6)),

        create_week(date(2026, 7, 13)),

    ]

    builder = MonthlyBuilder(weeks)

    july = builder.month(2026, 7)

    assert july is not None

    assert july.year == 2026
    assert july.month == 7

    assert len(july.weeks) == 2


# ======================================================

def test_missing_month():

    builder = MonthlyBuilder([])

    assert builder.month(2030, 1) is None


# ======================================================

def test_repr():

    weeks = [

        create_week(date(2026, 7, 6))

    ]

    builder = MonthlyBuilder(weeks)

    assert "MonthlyBuilder" in repr(builder)