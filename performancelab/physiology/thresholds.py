"""
PerformanceLab

Threshold Physiology

Utilities for physiological thresholds.
"""


# ======================================================
# Lactate Threshold Heart Rate
# ======================================================

def lthr(
    max_hr: float | None,
    percent: float = 90,
) -> float | None:

    if max_hr is None or max_hr <= 0:

        return None

    if percent <= 0:

        return None

    return max_hr * percent / 100


# ======================================================
# Aerobic Threshold Heart Rate
# ======================================================

def aerobic_threshold(
    max_hr: float | None,
    percent: float = 80,
) -> float | None:

    if max_hr is None or max_hr <= 0:

        return None

    if percent <= 0:

        return None

    return max_hr * percent / 100


# ======================================================
# Anaerobic Threshold Heart Rate
# ======================================================

def anaerobic_threshold(
    max_hr: float | None,
    percent: float = 90,
) -> float | None:

    if max_hr is None or max_hr <= 0:

        return None

    if percent <= 0:

        return None

    return max_hr * percent / 100


# ======================================================
# Threshold Pace
# ======================================================

def threshold_pace(
    distance: float | None,
    duration_hours: float | None,
) -> float | None:

    if distance is None or duration_hours is None:

        return None

    if distance <= 0 or duration_hours <= 0:

        return None

    return duration_hours / distance


# ======================================================
# Threshold Speed
# ======================================================

def threshold_speed(
    distance: float | None,
    duration_hours: float | None,
) -> float | None:

    if distance is None or duration_hours is None:

        return None

    if distance <= 0 or duration_hours <= 0:

        return None

    return distance / duration_hours


# ======================================================
# Threshold Power
# ======================================================

def threshold_power(
    ftp: float | None,
) -> float | None:

    if ftp is None or ftp <= 0:

        return None

    return ftp