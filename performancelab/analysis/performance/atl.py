"""
PerformanceLab

Acute Training Load

Utilities for calculating acute training load from
daily training-load values.
"""

from collections.abc import Iterable

from ._ema import exponential_curve, exponential_load


DEFAULT_ATL_DAYS = 7


# ======================================================
# Acute Training Load
# ======================================================

def atl(
    daily_loads: Iterable[float],
    days: int = DEFAULT_ATL_DAYS,
) -> float:

    """
    Calculates Acute Training Load from daily loads.

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
# Acute Training Load Curve
# ======================================================

def atl_curve(
    daily_loads: Iterable[float],
    days: int = DEFAULT_ATL_DAYS,
) -> list[float]:

    """
    Returns the ATL value after every daily sample.
    """

    return exponential_curve(

        daily_loads,

        days,

    )