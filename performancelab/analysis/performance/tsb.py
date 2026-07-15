"""
PerformanceLab

Training Stress Balance (TSB)

TSB = CTL - ATL

Positive values:
    Fresh athlete

Negative values:
    Fatigued athlete
"""

from .ctl import ctl_curve
from .atl import atl_curve


# ======================================================

def training_stress_balance(ctl_value, atl_value):

    """
    Calculates Training Stress Balance.
    """

    return ctl_value - atl_value


# ======================================================

def tsb(ctl_value, atl_value):

    """
    Alias for Training Stress Balance.
    """

    return training_stress_balance(

        ctl_value,

        atl_value,

    )


# ======================================================

def form(ctl_value, atl_value):

    """
    Training form.

    Positive:
        Fresh

    Negative:
        Fatigued
    """

    return tsb(

        ctl_value,

        atl_value,

    )


# ======================================================

def fatigue(ctl_value, atl_value):

    """
    Acute fatigue.

    Positive values indicate ATL exceeds CTL.
    """

    return atl_value - ctl_value


# ======================================================

def tsb_curve(loads):

    """
    Returns daily TSB values.
    """

    ctl_values = ctl_curve(loads)

    atl_values = atl_curve(loads)

    return [

        tsb(c, a)

        for c, a in zip(

            ctl_values,

            atl_values,

        )

    ]