"""
PerformanceLab

Training Load

Utilities for calculating training load.
"""


# ======================================================
# Workout load (Session RPE)
# ======================================================

def workout_load(workout):

    duration = workout.duration
    rpe = workout.feedback.rpe

    if duration is None:

        return None

    if rpe is None:

        return None

    minutes = duration.total_seconds() / 60

    return minutes * rpe


# ======================================================
# Weekly load
# ======================================================

def weekly_load(week):

    total = 0.0

    for workout in week.history:

        value = workout_load(workout)

        if value is not None:

            total += value

    return total


# ======================================================
# Monthly load
# ======================================================

def monthly_load(month):

    return sum(

        weekly_load(week)

        for week in month.weeks

    )