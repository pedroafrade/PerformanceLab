"""
PerformanceLab

Pace Physiology

Utilities for running pace and speed.
"""

from datetime import timedelta


# ======================================================
# Speed
# ======================================================

def speed(distance, duration):

    """
    Returns speed in km/h.
    """

    if (
        distance is None
        or duration is None
        or duration.total_seconds() == 0
    ):

        return None

    hours = duration.total_seconds() / 3600

    return distance / hours


# ======================================================
# Pace
# ======================================================

def pace(distance, duration):

    """
    Returns pace (minutes per kilometre).

    Example

    5.0 = 5:00 min/km
    """

    if (
        distance is None
        or duration is None
        or distance == 0
    ):

        return None

    minutes = duration.total_seconds() / 60

    return minutes / distance


# ======================================================
# Duration from Pace
# ======================================================

def duration(distance, pace):

    """
    Returns timedelta.
    """

    if (
        distance is None
        or pace is None
    ):

        return None

    minutes = distance * pace

    return timedelta(minutes=minutes)


# ======================================================
# Pace from Speed
# ======================================================

def pace_from_speed(speed):

    """
    Speed (km/h) -> pace (min/km)
    """

    if speed in (None, 0):

        return None

    return 60 / speed


# ======================================================
# Speed from Pace
# ======================================================

def speed_from_pace(pace):

    """
    Pace (min/km) -> speed (km/h)
    """

    if pace in (None, 0):

        return None

    return 60 / pace


# ======================================================
# Fastest Pace
# ======================================================

def fastest(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return min(values)


# ======================================================
# Slowest Pace
# ======================================================

def slowest(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return max(values)


# ======================================================
# Average Pace
# ======================================================

def average(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return sum(values) / len(values)