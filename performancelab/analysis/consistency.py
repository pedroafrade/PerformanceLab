"""
PerformanceLab

Consistency Analytics

Utilities for training consistency.
"""

from collections import Counter
from datetime import datetime

from . import time


# ======================================================
# Date normalization
# ======================================================

def _calendar_date(value):

    if isinstance(value, datetime):

        return value.date()

    return value


# ======================================================
# Unique training dates
# ======================================================

def _training_dates(history):

    return sorted({

        _calendar_date(workout.date)

        for workout in history

        if workout.date is not None

    })


# ======================================================
# Number of training days
# ======================================================

def training_days(history):

    return time.training_days(history)


# ======================================================
# Current streak
# ======================================================

def current_streak(history):

    dates = _training_dates(history)

    if not dates:

        return 0

    streak = 1

    for index in range(

        len(dates) - 1,

        0,

        -1,

    ):

        difference = (

            dates[index]

            - dates[index - 1]

        ).days

        if difference == 1:

            streak += 1

        else:

            break

    return streak


# ======================================================
# Longest streak
# ======================================================

def longest_streak(history):

    dates = _training_dates(history)

    if not dates:

        return 0

    longest = 1
    current = 1

    for index in range(1, len(dates)):

        difference = (

            dates[index]

            - dates[index - 1]

        ).days

        if difference == 1:

            current += 1

            longest = max(

                longest,

                current,

            )

        else:

            current = 1

    return longest


# ======================================================
# Workouts per weekday
# ======================================================

def weekday_distribution(history):

    counter = Counter()

    for workout in history:

        if workout.date is None:

            continue

        workout_date = _calendar_date(

            workout.date

        )

        counter[workout_date.weekday()] += 1

    return dict(counter)