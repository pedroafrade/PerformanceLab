"""
PerformanceLab

Threshold Physiology

Utilities for physiological thresholds.
"""


# ======================================================
# Lactate Threshold Heart Rate
# ======================================================

def lthr(max_hr, percent=90):

    if max_hr is None:

        return None

    return max_hr * percent / 100


# ======================================================
# Aerobic Threshold Heart Rate
# ======================================================

def aerobic_threshold(max_hr, percent=80):

    if max_hr is None:

        return None

    return max_hr * percent / 100


# ======================================================
# Anaerobic Threshold Heart Rate
# ======================================================

def anaerobic_threshold(max_hr, percent=90):

    if max_hr is None:

        return None

    return max_hr * percent / 100


# ======================================================
# Threshold Pace
# ======================================================

def threshold_pace(distance, duration_hours):

    if (
        distance in (None, 0)
        or duration_hours in (None, 0)
    ):

        return None

    return duration_hours / distance


# ======================================================
# Threshold Speed
# ======================================================

def threshold_speed(distance, duration_hours):

    if (
        distance is None
        or duration_hours in (None, 0)
    ):

        return None

    return distance / duration_hours


# ======================================================
# Threshold Power
# ======================================================

def threshold_power(ftp):

    return ftp