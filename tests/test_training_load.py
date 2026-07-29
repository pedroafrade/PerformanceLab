"""
PerformanceLab

Tests for Training Load.
"""

from datetime import date, timedelta

from performancelab import Workout
from performancelab.training import (
    WeeklySummary,
    MonthlySummary,
)
from performancelab.training.planning import (
    PlannedWorkout,
)
from performancelab.training.load import (
    workout_load,
    weekly_load,
    monthly_load,
    planned_workout_rpe,
    planned_workout_load,
    planned_weekly_load,
)


# ======================================================
# Helpers
# ======================================================

def create_workout(duration, rpe):

    workout = Workout()

    workout.info.date = date.today()
    workout.info.duration = duration

    workout.feedback.rpe = rpe

    return workout


# ======================================================

def create_week():

    week = WeeklySummary(

        start_date=date(2026, 7, 6),

        end_date=date(2026, 7, 12),

    )

    return week


# ======================================================
# Workout
# ======================================================

def test_workout_load():

    workout = create_workout(

        timedelta(hours=1),

        5,

    )

    assert workout_load(workout) == 300


# ======================================================

def test_workout_load_uses_estimated_rpe():

    workout = create_workout(
        timedelta(hours=1),
        None,
    )

    workout.feedback.estimated_rpe = 6

    assert workout_load(workout) == 360


# ======================================================

def test_manual_rpe_has_priority_for_workout_load():

    workout = create_workout(
        timedelta(hours=1),
        5,
    )

    workout.feedback.estimated_rpe = 8

    assert workout_load(workout) == 300


# ======================================================

def test_workout_without_duration():

    workout = create_workout(

        None,

        5,

    )

    assert workout_load(workout) is None


# ======================================================

def test_workout_without_rpe():

    workout = create_workout(

        timedelta(hours=1),

        None,

    )

    assert workout_load(workout) is None


# ======================================================
# Weekly
# ======================================================

def test_weekly_load():

    week = create_week()

    week.history.add(

        create_workout(

            timedelta(hours=1),

            5,

        )

    )

    week.history.add(

        create_workout(

            timedelta(minutes=30),

            8,

        )

    )

    assert weekly_load(week) == 540


# ======================================================

def test_empty_week():

    week = create_week()

    assert weekly_load(week) == 0


# ======================================================
# Monthly
# ======================================================

def test_monthly_load():

    week1 = create_week()

    week1.history.add(

        create_workout(

            timedelta(hours=1),

            5,

        )

    )

    week2 = WeeklySummary(

        start_date=date(2026, 7, 13),

        end_date=date(2026, 7, 19),

    )

    week2.history.add(

        create_workout(

            timedelta(hours=2),

            4,

        )

    )

    month = MonthlySummary(

        year=2026,

        month=7,

    )

    month.add_week(week1)

    month.add_week(week2)

    assert monthly_load(month) == 780


# ======================================================

def test_empty_month():

    month = MonthlySummary(

        year=2026,

        month=7,

    )

    assert monthly_load(month) == 0


# ======================================================
# Planned workouts
# ======================================================

def test_planned_easy_workout_load():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=timedelta(
            hours=1,
        ),
        intensity="Easy",
    )

    assert (
        planned_workout_rpe(workout)
        == 3.0
    )

    assert (
        planned_workout_load(workout)
        == 180
    )


def test_planned_hard_workout_load():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=timedelta(
            hours=1,
        ),
        intensity="Hard",
    )

    assert (
        planned_workout_rpe(workout)
        == 7.0
    )

    assert (
        planned_workout_load(workout)
        == 420
    )


def test_planned_long_workout_load():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=timedelta(
            minutes=90,
        ),
        intensity="Easy to moderate",
    )

    assert (
        planned_workout_load(workout)
        == 360
    )


def test_planned_load_normalizes_intensity():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=timedelta(
            minutes=30,
        ),
        intensity="  VERY EASY  ",
    )

    assert (
        planned_workout_load(workout)
        == 60
    )


def test_planned_workout_without_duration_has_no_load():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=None,
        intensity="Easy",
    )

    assert (
        planned_workout_load(workout)
        is None
    )


def test_unknown_planned_intensity_has_no_load():

    workout = PlannedWorkout(
        scheduled_at=date(
            2026,
            7,
            29,
        ),
        duration=timedelta(
            minutes=60,
        ),
        intensity="Unknown",
    )

    assert (
        planned_workout_load(workout)
        is None
    )
def test_planned_weekly_load():

    workouts = (
        PlannedWorkout(
            scheduled_at=date(
                2026,
                7,
                29,
            ),
            duration=timedelta(
                hours=1,
            ),
            intensity="Easy",
        ),
        PlannedWorkout(
            scheduled_at=date(
                2026,
                7,
                31,
            ),
            duration=timedelta(
                minutes=30,
            ),
            intensity="Hard",
        ),
    )

    assert planned_weekly_load(
        workouts
    ) == 390


def test_planned_weekly_load_ignores_unknown_load():

    workouts = (
        PlannedWorkout(
            scheduled_at=date(
                2026,
                7,
                29,
            ),
            duration=timedelta(
                hours=1,
            ),
            intensity="Easy",
        ),
        PlannedWorkout(
            scheduled_at=date(
                2026,
                7,
                31,
            ),
            duration=None,
            intensity="Race effort",
        ),
    )

    assert planned_weekly_load(
        workouts
    ) == 180


def test_empty_planned_week_has_zero_load():

    assert planned_weekly_load(
        ()
    ) == 0.0