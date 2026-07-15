"""
PerformanceLab

Pace Physiology

Utilities for running pace and speed.
"""

from collections.abc import Iterable
from datetime import timedelta


# ======================================================
# Speed
# ======================================================

def speed(
    distance: float | None,
    elapsed: timedelta | None,
) -> float | None:

    """
    Returns speed in kilometres per hour.
    """

    if distance is None or elapsed is None:

        return None

    if distance <= 0 or elapsed.total_seconds() <= 0:

        return None

    hours = elapsed.total_seconds() / 3600

    return distance / hours


# ======================================================
# Pace
# ======================================================

def pace(
    distance: float | None,
    elapsed: timedelta | None,
) -> float | None:

    """
    Returns pace in minutes per kilometre.

    Example:
        5.0 represents 5:00 min/km.
    """

    if distance is None or elapsed is None:

        return None

    if distance <= 0 or elapsed.total_seconds() <= 0:

        return None

    minutes = elapsed.total_seconds() / 60

    return minutes / distance


# ======================================================
# Duration from Pace
# ======================================================

def duration(
    distance: float | None,
    pace_value: float | None,
) -> timedelta | None:

    """
    Returns duration for a distance and pace.
    """

    if distance is None or pace_value is None:

        return None

    if distance <= 0 or pace_value <= 0:

        return None

    minutes = distance * pace_value

    return timedelta(minutes=minutes)


# ======================================================
# Pace from Speed
# ======================================================

def pace_from_speed(
    speed_value: float | None,
) -> float | None:

    """
    Converts speed in km/h to pace in min/km.
    """

    if speed_value is None or speed_value <= 0:

        return None

    return 60 / speed_value


# ======================================================
# Speed from Pace
# ======================================================

def speed_from_pace(
    pace_value: float | None,
) -> float | None:

    """
    Converts pace in min/km to speed in km/h.
    """

    if pace_value is None or pace_value <= 0:

        return None

    return 60 / pace_value


# ======================================================
# Fastest Pace
# ======================================================

def fastest(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value > 0

    ]

    if not valid_values:

        return None

    return min(valid_values)


# ======================================================
# Slowest Pace
# ======================================================

def slowest(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value > 0

    ]

    if not valid_values:

        return None

    return max(valid_values)


# ======================================================
# Average Pace
# ======================================================

def average(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value > 0

    ]

    if not valid_values:

        return None

    return sum(valid_values) / len(valid_values)