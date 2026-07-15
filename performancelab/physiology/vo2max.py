"""
PerformanceLab

VO2max Physiology

Utilities for estimating VO₂max and oxygen demand.
"""

import math


# ======================================================
# Cooper Test
# ======================================================

def vo2max_from_cooper(distance):

    """
    Cooper 12-minute test.

    distance in metres.
    """

    if distance is None:

        return None

    return (distance - 504.9) / 44.73


# ======================================================
# Running Speed
# ======================================================

def vo2max_from_speed(speed):

    """
    Estimates oxygen consumption from running speed.

    ACSM running equation (level ground).

    speed in km/h.
    """

    if speed is None:

        return None

    speed_m_min = speed * 1000 / 60

    return (0.2 * speed_m_min + 3.5)


# ======================================================
# Oxygen Cost
# ======================================================

def oxygen_cost(speed):

    """
    Alias for ACSM oxygen demand.

    speed in km/h.
    """

    return vo2max_from_speed(speed)


# ======================================================
# Running Economy
# ======================================================

def running_economy(speed, vo2):

    """
    Running economy.

    Lower is generally better.

    Returns ml/kg/km.
    """

    if (

        speed is None

        or vo2 is None

        or speed == 0

    ):

        return None

    km_per_min = speed / 60

    return vo2 / km_per_min


# ======================================================
# Daniels VDOT
# ======================================================

def vdot(speed):

    """
    Simplified Daniels VDOT approximation.

    speed in km/h.
    """

    if speed is None:

        return None

    return vo2max_from_speed(speed)


# ======================================================
# Relative Intensity
# ======================================================

def relative_intensity(vo2, vo2max):

    """
    Returns %VO2max.
    """

    if (

        vo2 is None

        or vo2max in (None, 0)

    ):

        return None

    return (vo2 / vo2max) * 100


# ======================================================
# VO2 Reserve
# ======================================================

def vo2_reserve(vo2max, resting=3.5):

    """
    VO2 Reserve.
    """

    if vo2max is None:

        return None

    return vo2max - resting