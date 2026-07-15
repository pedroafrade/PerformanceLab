"""
PerformanceLab

VO2max Physiology

Utilities for estimating VO₂max and oxygen demand.
"""


# ======================================================
# Cooper Test
# ======================================================

def vo2max_from_cooper(
    distance: float | None,
) -> float | None:

    """
    Estimates VO₂max from the Cooper 12-minute test.

    Parameters
    ----------
    distance:
        Distance covered in metres during 12 minutes.

    Returns
    -------
    Estimated VO₂max in ml/kg/min.
    """

    if distance is None or distance <= 0:

        return None

    estimate = (

        distance - 504.9

    ) / 44.73

    if estimate <= 0:

        return None

    return estimate


# ======================================================
# Running Oxygen Cost
# ======================================================

def oxygen_cost(
    speed: float | None,
) -> float | None:

    """
    Estimates oxygen demand for level running.

    Parameters
    ----------
    speed:
        Running speed in kilometres per hour.

    Returns
    -------
    Oxygen demand in ml/kg/min.

    This estimates the oxygen cost of running at the given
    speed. It does not, by itself, estimate the athlete's
    VO₂max.
    """

    if speed is None or speed <= 0:

        return None

    speed_m_min = speed * 1000 / 60

    return (

        0.2 * speed_m_min

        + 3.5

    )


# ======================================================
# Legacy Speed Estimate
# ======================================================

def vo2max_from_speed(
    speed: float | None,
) -> float | None:

    """
    Backwards-compatible alias for oxygen_cost().

    Despite its historical name in PerformanceLab, this
    function estimates running oxygen demand rather than
    an athlete's VO₂max.
    """

    return oxygen_cost(speed)


# ======================================================
# Running Economy
# ======================================================

def running_economy(
    speed: float | None,
    vo2: float | None,
) -> float | None:

    """
    Calculates oxygen cost per kilometre.

    Parameters
    ----------
    speed:
        Running speed in kilometres per hour.

    vo2:
        Oxygen consumption in ml/kg/min.

    Returns
    -------
    Running economy in ml/kg/km.

    Lower values indicate less oxygen consumed per
    kilometre at the specified speed.
    """

    if speed is None or vo2 is None:

        return None

    if speed <= 0 or vo2 <= 0:

        return None

    kilometres_per_minute = speed / 60

    return vo2 / kilometres_per_minute


# ======================================================
# Legacy VDOT Approximation
# ======================================================

def vdot(
    speed: float | None,
) -> float | None:

    """
    Legacy simplified estimate based only on running speed.

    A complete Daniels VDOT calculation also requires the
    duration of a race or time trial. This function is kept
    temporarily for backwards compatibility.
    """

    return oxygen_cost(speed)


# ======================================================
# Relative Intensity
# ======================================================

def relative_intensity(
    vo2: float | None,
    vo2max: float | None,
) -> float | None:

    """
    Returns oxygen consumption as a percentage of VO₂max.
    """

    if vo2 is None or vo2max is None:

        return None

    if vo2 < 0 or vo2max <= 0:

        return None

    return (

        vo2

        / vo2max

        * 100

    )


# ======================================================
# VO2 Reserve
# ======================================================

def vo2_reserve(
    vo2max: float | None,
    resting: float = 3.5,
) -> float | None:

    """
    Calculates VO₂ reserve.

    VO₂ reserve = VO₂max - resting VO₂.
    """

    if vo2max is None:

        return None

    if resting < 0 or vo2max <= resting:

        return None

    return vo2max - resting