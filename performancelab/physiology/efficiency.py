"""
PerformanceLab

Efficiency Physiology

Utilities for measuring training efficiency.
"""


# ======================================================
# Speed per Heart Rate
# ======================================================

def speed_per_heart_rate(
    speed: float | None,
    heart_rate: float | None,
) -> float | None:

    """
    Returns kilometres per hour per beat per minute.
    """

    if speed is None or heart_rate is None:

        return None

    if speed < 0 or heart_rate <= 0:

        return None

    return speed / heart_rate


# ======================================================
# Power per Heart Rate
# ======================================================

def power_per_heart_rate(
    power: float | None,
    heart_rate: float | None,
) -> float | None:

    """
    Returns watts per beat per minute.
    """

    if power is None or heart_rate is None:

        return None

    if power < 0 or heart_rate <= 0:

        return None

    return power / heart_rate


# ======================================================
# Speed per Watt
# ======================================================

def speed_per_watt(
    speed: float | None,
    power: float | None,
) -> float | None:

    """
    Returns kilometres per hour per watt.
    """

    if speed is None or power is None:

        return None

    if speed < 0 or power <= 0:

        return None

    return speed / power


# ======================================================
# Vertical Speed
# ======================================================

def vertical_speed(
    elevation_gain: float | None,
    duration_hours: float | None,
) -> float | None:

    """
    Returns vertical ascent speed in metres per hour.
    """

    if elevation_gain is None or duration_hours is None:

        return None

    if elevation_gain < 0 or duration_hours <= 0:

        return None

    return elevation_gain / duration_hours


# ======================================================
# Efficiency Factor
# ======================================================

def efficiency_factor(
    normalized_power: float | None,
    average_heart_rate: float | None,
) -> float | None:

    """
    Returns cycling efficiency factor.

    Conventionally:

        normalized power / average heart rate
    """

    return power_per_heart_rate(

        normalized_power,

        average_heart_rate,

    )


# ======================================================
# Normalized Efficiency
# ======================================================

def normalized_efficiency(
    value: float | None,
    reference: float | None,
) -> float | None:

    """
    Returns efficiency relative to a reference percentage.
    """

    if value is None or reference is None:

        return None

    if value < 0 or reference <= 0:

        return None

    return (

        value

        / reference

        * 100

    )