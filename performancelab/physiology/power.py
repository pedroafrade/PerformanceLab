"""
PerformanceLab

Power Physiology

Utilities for power calculations.
"""

from collections.abc import Iterable


# ======================================================
# Relative Power
# ======================================================

def relative_power(
    power: float | None,
    weight: float | None,
) -> float | None:

    if power is None or weight is None:

        return None

    if weight <= 0:

        return None

    return power / weight


# ======================================================
# Percentage of FTP
# ======================================================

def percent_ftp(
    power: float | None,
    ftp: float | None,
) -> float | None:

    if power is None or ftp is None:

        return None

    if ftp <= 0:

        return None

    return (

        power

        / ftp

        * 100

    )


# ======================================================
# Functional Threshold Power from W/kg
# ======================================================

def ftp_from_relative(
    relative: float | None,
    weight: float | None,
) -> float | None:

    if relative is None or weight is None:

        return None

    if weight <= 0:

        return None

    return relative * weight


# ======================================================
# Average Power
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


# ======================================================
# Peak Power
# ======================================================

def peak(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None

    ]

    if not valid_values:

        return None

    return max(valid_values)


# ======================================================
# Minimum Power
# ======================================================

def minimum(
    values: Iterable[float | None],
) -> float | None:

    valid_values = [

        value

        for value in values

        if value is not None

    ]

    if not valid_values:

        return None

    return min(valid_values)