"""
PerformanceLab

Training Zones

Utilities for physiological training zones.
"""

from collections.abc import Mapping

from .heartrate import karvonen


ZoneRange = tuple[float, float]
ZoneMap = dict[str, ZoneRange]


# ======================================================
# Heart Rate Zones (Karvonen)
# ======================================================

def heart_rate_zones(
    max_hr: float | None,
    resting_hr: float | None,
) -> ZoneMap | None:

    if max_hr is None or resting_hr is None:

        return None

    if max_hr <= 0 or resting_hr < 0:

        return None

    if max_hr <= resting_hr:

        return None

    return {

        "Z1": (
            karvonen(50, max_hr, resting_hr),
            karvonen(60, max_hr, resting_hr),
        ),

        "Z2": (
            karvonen(60, max_hr, resting_hr),
            karvonen(70, max_hr, resting_hr),
        ),

        "Z3": (
            karvonen(70, max_hr, resting_hr),
            karvonen(80, max_hr, resting_hr),
        ),

        "Z4": (
            karvonen(80, max_hr, resting_hr),
            karvonen(90, max_hr, resting_hr),
        ),

        "Z5": (
            karvonen(90, max_hr, resting_hr),
            karvonen(100, max_hr, resting_hr),
        ),

    }


# ======================================================
# Power Zones (FTP)
# ======================================================

def power_zones(
    ftp: float | None,
) -> ZoneMap | None:

    if ftp is None or ftp <= 0:

        return None

    return {

        "Z1": (
            0.00 * ftp,
            0.55 * ftp,
        ),

        "Z2": (
            0.55 * ftp,
            0.75 * ftp,
        ),

        "Z3": (
            0.75 * ftp,
            0.90 * ftp,
        ),

        "Z4": (
            0.90 * ftp,
            1.05 * ftp,
        ),

        "Z5": (
            1.05 * ftp,
            1.20 * ftp,
        ),

    }


# ======================================================
# Pace Zones
# ======================================================

def pace_zones(
    threshold_pace: float | None,
) -> ZoneMap | None:

    if threshold_pace is None or threshold_pace <= 0:

        return None

    return {

        "Z1": (
            threshold_pace * 1.30,
            threshold_pace * 1.20,
        ),

        "Z2": (
            threshold_pace * 1.20,
            threshold_pace * 1.10,
        ),

        "Z3": (
            threshold_pace * 1.10,
            threshold_pace * 1.05,
        ),

        "Z4": (
            threshold_pace * 1.05,
            threshold_pace * 1.00,
        ),

        "Z5": (
            threshold_pace * 1.00,
            threshold_pace * 0.90,
        ),

    }


# ======================================================
# Zone Lookup
# ======================================================

def zone(
    value: float | None,
    zones: Mapping[str, ZoneRange] | None,
) -> str | None:

    if value is None or zones is None:

        return None

    for name, limits in zones.items():

        lower = min(limits)
        upper = max(limits)

        if lower <= value <= upper:

            return name

    return None