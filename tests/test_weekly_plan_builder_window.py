"""
PerformanceLab

Tests for WeeklyPlanBuilder.window().
"""

from datetime import date, datetime, timedelta

from performancelab.training.planning.planned_workout import (
    PlannedWorkout,
)
from performancelab.training.planning.weekly_plan_builder import (
    WeeklyPlanBuilder,
)


def workout(day: date, title: str):

    return PlannedWorkout(
        scheduled_at=datetime.combine(
            day,
            datetime.min.time(),
        ),
        sport="Running",
        title=title,
        duration=timedelta(hours=1),
    )


def test_window_is_centered_on_requested_day():

    center = date(2025, 7, 31)

    plan = WeeklyPlanBuilder().window(center)

    assert plan.start_date == date(2025, 7, 28)
    assert plan.end_date == date(2025, 8, 3)


def test_window_returns_only_workouts_inside_range():

    center = date(2025, 7, 31)

    builder = WeeklyPlanBuilder(
        [
            workout(date(2025, 7, 27), "outside-before"),
            workout(date(2025, 7, 28), "inside-1"),
            workout(date(2025, 7, 31), "inside-2"),
            workout(date(2025, 8, 3), "inside-3"),
            workout(date(2025, 8, 4), "outside-after"),
        ]
    )

    plan = builder.window(center)

    assert [w.title for w in plan.workouts] == [
        "inside-1",
        "inside-2",
        "inside-3",
    ]


def test_window_accepts_datetime():

    center = datetime(
        2025,
        7,
        31,
        15,
        45,
    )

    plan = WeeklyPlanBuilder().window(center)

    assert plan.start_date == date(2025, 7, 28)
    assert plan.end_date == date(2025, 8, 3)


def test_week_method_is_unchanged():

    day = date(2025, 7, 31)

    plan = WeeklyPlanBuilder().week(day)

    assert plan.start_date == date(2025, 7, 28)
    assert plan.end_date == date(2025, 8, 3)