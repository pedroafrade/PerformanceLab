"""
PerformanceLab

Cadence Physiology

Utilities for cadence calculations.
"""


# ======================================================
# Average Cadence
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


# ======================================================
# Maximum Cadence
# ======================================================

def maximum(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return max(values)


# ======================================================
# Minimum Cadence
# ======================================================

def minimum(values):

    values = [

        value

        for value in values

        if value is not None

    ]

    if not values:

        return None

    return min(values)


# ======================================================
# Cadence Reserve
# ======================================================

def cadence_reserve(maximum, average):

    if maximum is None or average is None:

        return None

    return maximum - average


# ======================================================
# Percentage of Maximum Cadence
# ======================================================

def percent_maximum(cadence, maximum):

    if cadence is None or maximum in (None, 0):

        return None

    return (cadence / maximum) * 100


# ======================================================
# Recommended Running Cadence
# ======================================================

def recommended_running():

    """
    Typical running cadence range (spm).
    """

    return (170, 190)


# ======================================================
# Recommended Cycling Cadence
# ======================================================

def recommended_cycling():

    """
    Typical cycling cadence range (rpm).
    """

    return (80, 100)