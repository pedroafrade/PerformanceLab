"""
PerformanceLab

Efficiency Physiology

Utilities for measuring training efficiency.
"""


# ======================================================
# Speed per Heart Rate
# ======================================================

def speed_per_heart_rate(speed, heart_rate):

    """
    km/h per bpm.
    """

    if (

        speed is None

        or heart_rate in (None, 0)

    ):

        return None

    return speed / heart_rate


# ======================================================
# Power per Heart Rate
# ======================================================

def power_per_heart_rate(power, heart_rate):

    """
    Watts per bpm.
    """

    if (

        power is None

        or heart_rate in (None, 0)

    ):

        return None

    return power / heart_rate


# ======================================================
# Speed per Watt
# ======================================================

def speed_per_watt(speed, power):

    """
    km/h per watt.
    """

    if (

        speed is None

        or power in (None, 0)

    ):

        return None

    return speed / power


# ======================================================
# Vertical Speed
# ======================================================

def vertical_speed(elevation_gain, duration_hours):

    """
    Vertical ascent speed.

    metres/hour.
    """

    if (

        elevation_gain is None

        or duration_hours in (None, 0)

    ):

        return None

    return elevation_gain / duration_hours


# ======================================================
# Efficiency Factor
# ======================================================

def efficiency_factor(power, heart_rate):

    """
    Coggan Efficiency Factor.

    EF = Power / HR
    """

    return power_per_heart_rate(

        power,

        heart_rate,

    )


# ======================================================
# Normalised Efficiency
# ======================================================

def normalized_efficiency(value, reference):

    """
    Relative efficiency.

    Returns percentage.
    """

    if (

        value is None

        or reference in (None, 0)

    ):

        return None

    return (value / reference) * 100