"""
PerformanceLab

Heart Rate Physiology

Utilities for heart rate calculations.
"""

from collections.abc import Iterable


# ======================================================
# Heart Rate Reserve
# ======================================================

def heart_rate_reserve(
    max_hr: float | None,
    resting_hr: float | None,
) -> float | None:

    if max_hr is None or resting_hr is None:

        return None

    reserve = max_hr - resting_hr

    if reserve <= 0:

        return None

    return reserve


# ======================================================
# Percentage of Maximum Heart Rate
# ======================================================

def percent_max_hr(
    hr: float | None,
    max_hr: float | None,
) -> float | None:

    if hr is None or max_hr is None:

        return None

    if max_hr <= 0:

        return None

    return (

        hr

        / max_hr

        * 100

    )


# ======================================================
# Percentage of Heart Rate Reserve (Karvonen)
# ======================================================

def percent_hrr(
    hr: float | None,
    max_hr: float | None,
    resting_hr: float | None,
) -> float | None:

    if hr is None or resting_hr is None:

        return None

    reserve = heart_rate_reserve(

        max_hr,

        resting_hr,

    )

    if reserve is None:

        return None

    return (

        (hr - resting_hr)

        / reserve

        * 100

    )


# ======================================================
# Karvonen Target Heart Rate
# ======================================================

def karvonen(
    percent: float | None,
    max_hr: float | None,
    resting_hr: float | None,
) -> float | None:

    if percent is None or resting_hr is None:

        return None

    reserve = heart_rate_reserve(

        max_hr,

        resting_hr,

    )

    if reserve is None:

        return None

    return resting_hr + (

        reserve

        * percent

        / 100

    )


# ======================================================
# Average Heart Rate
# ======================================================

def average(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None

    ]

    if not valid_values:

        return None

    return sum(valid_values) / len(valid_values)