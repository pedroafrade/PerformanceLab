"""
PerformanceLab

Recovery Physiology

Utilities related to recovery.
"""

from datetime import timedelta


# ======================================================
# Recovery Score
# ======================================================

def recovery_score(rpe):

    """
    Returns a simple recovery score (0-100).

    Higher is better.
    """

    if rpe is None:

        return None

    score = 100 - (rpe * 10)

    return max(0, min(100, score))


# ======================================================
# Suggested Recovery Days
# ======================================================

def recovery_days(rpe):

    """
    Suggested recovery days based on RPE.
    """

    if rpe is None:

        return None

    if rpe <= 3:

        return 0

    if rpe <= 5:

        return 1

    if rpe <= 7:

        return 2

    if rpe <= 9:

        return 3

    return 4


# ======================================================
# Heart Rate Recovery
# ======================================================

def heart_rate_recovery(max_hr, hr_after_1min):

    """
    Heart-rate recovery after one minute.

    Higher values are generally better.
    """

    if (

        max_hr is None

        or hr_after_1min is None

    ):

        return None

    return max_hr - hr_after_1min


# ======================================================
# Recovered?
# ======================================================

def is_recovered(days_since_last_workout, required_days):

    if (

        days_since_last_workout is None

        or required_days is None

    ):

        return None

    return days_since_last_workout >= required_days


# ======================================================
# Training Strain
# ======================================================

def training_strain(duration: timedelta, rpe):

    """
    Session-RPE method.

    Strain = minutes × RPE
    """

    if (

        duration is None

        or rpe is None

    ):

        return None

    minutes = duration.total_seconds() / 60

    return minutes * rpe