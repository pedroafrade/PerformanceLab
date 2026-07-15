"""
PerformanceLab

Internal Exponential Moving Average utilities.
"""

from math import exp


# ======================================================

def decay_constant(days):

    """
    Exponential decay constant.
    """

    return 1 - exp(-1 / days)


# ======================================================

def exponential_load(loads, days):

    """
    Exponential moving average.
    """

    loads = list(loads)

    if not loads:

        return 0.0

    alpha = decay_constant(days)

    value = loads[0]

    for load in loads[1:]:

        value += alpha * (load - value)

    return value


# ======================================================

def exponential_curve(loads, days):

    """
    Returns EMA after every sample.
    """

    loads = list(loads)

    if not loads:

        return []

    alpha = decay_constant(days)

    current = loads[0]

    values = [current]

    for load in loads[1:]:

        current += alpha * (load - current)

        values.append(current)

    return values