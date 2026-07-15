"""
PerformanceLab

Training Zones

Utilities for physiological training zones.
"""

from .heartrate import karvonen


# ======================================================
# Heart Rate Zones (Karvonen)
# ======================================================

def heart_rate_zones(max_hr, resting_hr):

    if max_hr is None or resting_hr is None:

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

def power_zones(ftp):

    if ftp is None:

        return None

    return {

        "Z1": (0.00 * ftp, 0.55 * ftp),

        "Z2": (0.55 * ftp, 0.75 * ftp),

        "Z3": (0.75 * ftp, 0.90 * ftp),

        "Z4": (0.90 * ftp, 1.05 * ftp),

        "Z5": (1.05 * ftp, 1.20 * ftp),

    }


# ======================================================
# Pace Zones
# ======================================================

def pace_zones(threshold_pace):

    if threshold_pace is None:

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

def zone(value, zones):

    if value is None or zones is None:

        return None

    for name, (minimum, maximum) in zones.items():

        if minimum <= value <= maximum:

            return name

    return None