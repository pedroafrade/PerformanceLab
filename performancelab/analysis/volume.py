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

        workout.distance or 0

        for workout in history

    )


# ======================================================
# Total duration
# ======================================================

def total_duration(history):

    total = timedelta()

    for workout in history:

        if workout.duration is not None:

            total += workout.duration

    return total


# ======================================================
# Total elevation gain
# ======================================================

def total_elevation(history):

    return sum(

        workout.elevation_gain or 0

        for workout in history

    )


# ======================================================
# Average distance
# ======================================================

def average_distance(history):

    values = [

        workout.distance

        for workout in history

        if workout.distance is not None

    ]

    if not values:

        return None

    return sum(values) / len(values)


# ======================================================
# Average duration
# ======================================================

def average_duration(history):

    values = [

        workout.duration

        for workout in history

        if workout.duration is not None

    ]

    if not values:

        return None

    return sum(values, timedelta()) / len(values)


# ======================================================
# Average elevation gain
# ======================================================

def average_elevation(history):

    values = [

        workout.elevation_gain

        for workout in history

        if workout.elevation_gain is not None

    ]

    if not values:

        return None

    return sum(values) / len(values)