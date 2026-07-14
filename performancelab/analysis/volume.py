"""
PerformanceLab

Volume Analytics

Utilities for training volume calculations.
"""

from datetime import timedelta


# ======================================================
# Total distance
# ======================================================

def total_distance(history):

    return sum(

        workout.info.distance or 0

        for workout in history

    )


# ======================================================
# Total duration
# ======================================================

def total_duration(history):

    total = timedelta()

    for workout in history:

        duration = workout.info.duration

        if duration is not None:

            total += duration

    return total


# ======================================================
# Total elevation gain
# ======================================================

def total_elevation(history):

    return sum(

        workout.info.elevation_gain or 0

        for workout in history

    )


# ======================================================
# Average distance
# ======================================================

def average_distance(history):

    if len(history) == 0:

        return None

    return total_distance(history) / len(history)


# ======================================================
# Average duration
# ======================================================

def average_duration(history):

    if len(history) == 0:

        return None

    return total_duration(history) / len(history)


# ======================================================
# Average elevation gain
# ======================================================

def average_elevation(history):

    if len(history) == 0:

        return None

    return total_elevation(history) / len(history)