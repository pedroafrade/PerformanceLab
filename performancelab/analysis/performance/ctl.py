"""
PerformanceLab

Chronic Training Load

Utilities for calculating chronic training load from
daily training-load values.
"""

from collections.abc import Iterable

from ._ema import exponential_curve, exponential_load


DEFAULT_CTL_DAYS = 42


# ======================================================
# Chronic Training Load
# ======================================================

def ctl(
    daily_loads: Iterable[float],
    days: int = DEFAULT_CTL_DAYS,
) -> float:

    """
    Calculates Chronic Training Load from daily loads.

    Parameters
    ----------
    daily_loads:
        Chronological daily training-load values. Rest days
        should be represented by zero.

    days:
        Exponential time constant in days.
    """

    return exponential_load(

        daily_loads,

        days,

    )


# ======================================================
# Chronic Training Load Curve
# ======================================================

def ctl_curve(
    daily_loads: Iterable[float],
    days: int = DEFAULT_CTL_DAYS,
) -> list[float]:

    """
    Returns the CTL value after every daily sample.
    """

    return exponential_curve(

        daily_loads,

        days,

    )