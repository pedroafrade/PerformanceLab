"""
PerformanceLab

Internal Exponential Moving Average utilities.
"""

from collections.abc import Iterable
from math import exp


# ======================================================
# Decay constant
# ======================================================

def decay_constant(
    days: int | float,
) -> float:

    """
    Returns the exponential smoothing constant.

    Parameters
    ----------
    days:
        Positive time constant.
    """

    if days <= 0:

        raise ValueError(
            "days must be greater than zero"
        )

    return 1 - exp(-1 / days)


# ======================================================
# Load normalization
# ======================================================

def _normalize_loads(
    loads: Iterable[float | None],
) -> list[float]:

    values = []

    for load in loads:

        if load is None:

            values.append(0.0)

            continue

        if load < 0:

            raise ValueError(
                "training loads cannot be negative"
            )

        values.append(float(load))

    return values


# ======================================================
# Exponential load
# ======================================================

def exponential_load(
    loads: Iterable[float | None],
    days: int | float,
    initial: float = 0.0,
) -> float:

    """
    Returns the final exponential moving-average value.

    Missing loads are treated as zero-load days.
    """

    if initial < 0:

        raise ValueError(
            "initial value cannot be negative"
        )

    values = _normalize_loads(loads)

    if not values:

        return float(initial)

    alpha = decay_constant(days)

    current = float(initial)

    for load in values:

        current += alpha * (

            load - current

        )

    return current


# ======================================================
# Exponential curve
# ======================================================

def exponential_curve(
    loads: Iterable[float | None],
    days: int | float,
    initial: float = 0.0,
) -> list[float]:

    """
    Returns one EMA value after each sample.

    Missing loads are treated as zero-load days.
    """

    if initial < 0:

        raise ValueError(
            "initial value cannot be negative"
        )

    values = _normalize_loads(loads)

    if not values:

        return []

    alpha = decay_constant(days)

    current = float(initial)

    curve = []

    for load in values:

        current += alpha * (

            load - current

        )

        curve.append(current)

    return curve