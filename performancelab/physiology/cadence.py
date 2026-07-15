"""
PerformanceLab

Cadence Physiology

Utilities for cadence calculations.
"""

from collections.abc import Iterable


# ======================================================
# Average Cadence
# ======================================================

def average(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value >= 0

    ]

    if not valid_values:

        return None

    return sum(valid_values) / len(valid_values)


# ======================================================
# Maximum Cadence
# ======================================================

def maximum(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value >= 0

    ]

    if not valid_values:

        return None

    return max(valid_values)


# ======================================================
# Minimum Cadence
# ======================================================

def minimum(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None and value >= 0

    ]

    if not valid_values:

        return None

    return min(valid_values)


# ======================================================
# Cadence Reserve
# ======================================================

def cadence_reserve(
    maximum_cadence: float | None,
    average_cadence: float | None,
) -> float | None:

    if (

        maximum_cadence is None

        or average_cadence is None

    ):

        return None

    if (

        maximum_cadence < 0

        or average_cadence < 0

        or average_cadence > maximum_cadence

    ):

        return None

    return maximum_cadence - average_cadence


# ======================================================
# Percentage of Maximum Cadence
# ======================================================

def percent_maximum(
    cadence: float | None,
    maximum_cadence: float | None,
) -> float | None:

    if cadence is None or maximum_cadence is None:

        return None

    if cadence < 0 or maximum_cadence <= 0:

        return None

    return (

        cadence

        / maximum_cadence

        * 100

    )


# ======================================================
# Recommended Running Cadence
# ======================================================

def recommended_running() -> tuple[int, int]:

    """
    Returns a broad reference range in steps per minute.

    This is not an individualized recommendation.
    """

    return (170, 190)


# ======================================================
# Recommended Cycling Cadence
# ======================================================

def recommended_cycling() -> tuple[int, int]:

    """
    Returns a broad reference range in revolutions per minute.

    This is not an individualized recommendation.
    """

    return (80, 100)