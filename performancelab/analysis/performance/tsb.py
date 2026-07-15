"""
PerformanceLab

Training Stress Balance

TSB = CTL - ATL
"""

from collections.abc import Iterable

from .atl import atl_curve
from .ctl import ctl_curve


# ======================================================
# Training Stress Balance
# ======================================================

def training_stress_balance(
    ctl_value: float,
    atl_value: float,
) -> float:

    """
    Calculates Training Stress Balance.

    Positive values indicate that CTL exceeds ATL.
    Negative values indicate that ATL exceeds CTL.
    """

    return ctl_value - atl_value


# ======================================================
# TSB Alias
# ======================================================

def tsb(
    ctl_value: float,
    atl_value: float,
) -> float:

    return training_stress_balance(

        ctl_value,

        atl_value,

    )


# ======================================================
# Form Alias
# ======================================================

def form(
    ctl_value: float,
    atl_value: float,
) -> float:

    return training_stress_balance(

        ctl_value,

        atl_value,

    )


# ======================================================
# Fatigue Difference
# ======================================================

def fatigue(
    ctl_value: float,
    atl_value: float,
) -> float:

    """
    Returns ATL minus CTL.

    This is the inverse sign of TSB.
    """

    return atl_value - ctl_value


# ======================================================
# TSB Curve
# ======================================================

def tsb_curve(
    daily_loads: Iterable[float],
    ctl_days: int = 42,
    atl_days: int = 7,
) -> list[float]:

    """
    Returns one TSB value for each daily load.
    """

    loads = list(daily_loads)

    ctl_values = ctl_curve(

        loads,

        days=ctl_days,

    )

    atl_values = atl_curve(

        loads,

        days=atl_days,

    )

    return [

        training_stress_balance(

            ctl_value,

            atl_value,

        )

        for ctl_value, atl_value in zip(

            ctl_values,

            atl_values,

        )

    ]