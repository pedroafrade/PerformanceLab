"""
PerformanceLab

Training Load

Utilities for calculating training load.
"""

from datetime import timedelta


# ======================================================
# Workout load (Session RPE)
# ======================================================

def workout_load(workout):

    duration = workout.info.duration
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

        load = workout_load(workout)

        if load is not None:

            total += load

    return total


# ======================================================
# Monthly load
# ======================================================

def monthly_load(month):

    return sum(

        weekly_load(week)

        for week in month.weeks

    )