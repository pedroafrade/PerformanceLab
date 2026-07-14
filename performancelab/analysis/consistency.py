"""
PerformanceLab

Consistency Analytics

Utilities for training consistency.
"""

from collections import Counter


# ======================================================
# Number of training days
# ======================================================

def training_days(history):

    return len({

        workout.date

        for workout in history

        if workout.date is not None

    })


# ======================================================
# Current streak
# ======================================================

def current_streak(history):

    if len(history) == 0:

        return 0

    dates = sorted({

        workout.date

        for workout in history

        if workout.date is not None

    })

    streak = 1

    for i in range(len(dates) - 1, 0, -1):

        if (dates[i] - dates[i - 1]).days == 1:

            streak += 1

        else:

            break

    return streak


# ======================================================
# Longest streak
# ======================================================

def longest_streak(history):

    if len(history) == 0:

        return 0

    dates = sorted({

        workout.date

        for workout in history

        if workout.date is not None

    })

    longest = 1

    current = 1

    for i in range(1, len(dates)):

        if (dates[i] - dates[i - 1]).days == 1:

            current += 1

            longest = max(longest, current)

        else:

            current = 1

    return longest


# ======================================================
# Workouts per weekday
# ======================================================

def weekday_distribution(history):

    counter = Counter()

    for workout in history:

        if workout.date is not None:

            counter[workout.date.weekday()] += 1

    return dict(counter)