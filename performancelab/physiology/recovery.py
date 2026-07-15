"""
PerformanceLab

Recovery Physiology

Utilities related to recovery.
"""

from datetime import timedelta


# ======================================================
# RPE validation
# ======================================================

def _valid_rpe(rpe: float | None) -> bool:

    return (

        rpe is not None

        and 0 <= rpe <= 10

    )


# ======================================================
# Recovery Score
# ======================================================

def recovery_score(
    rpe: float | None,
) -> float | None:

    """
    Returns a simple RPE-derived score from 0 to 100.

    Higher values indicate lower perceived exertion.

    This is not a complete recovery assessment because
    it does not include sleep, soreness, stress, fatigue,
    heart-rate variability or recent training load.
    """

    if not _valid_rpe(rpe):

        return None

    return 100 - rpe * 10


# ======================================================
# Suggested Recovery Days
# ======================================================

def recovery_days(
    rpe: float | None,
) -> int | None:

    """
    Returns a simple recovery-time suggestion based on RPE.

    This is a heuristic, not an individualized physiological
    recovery prediction.
    """

    if not _valid_rpe(rpe):

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

def heart_rate_recovery(
    peak_hr: float | None,
    hr_after_1min: float | None,
) -> float | None:

    """
    Returns the heart-rate drop after one minute.

    Higher positive values indicate a larger reduction
    during the first minute of recovery.
    """

    if peak_hr is None or hr_after_1min is None:

        return None

    if peak_hr <= 0 or hr_after_1min < 0:

        return None

    if hr_after_1min > peak_hr:

        return None

    return peak_hr - hr_after_1min


# ======================================================
# Recovered?
# ======================================================

def is_recovered(
    days_since_last_workout: float | None,
    required_days: float | None,
) -> bool | None:

    if (

        days_since_last_workout is None

        or required_days is None

    ):

        return None

    if (

        days_since_last_workout < 0

        or required_days < 0

    ):

        return None

    return days_since_last_workout >= required_days


# ======================================================
# Training Strain
# ======================================================

def training_strain(
    elapsed: timedelta | None,
    rpe: float | None,
) -> float | None:

    """
    Calculates Session-RPE load.

    Strain = duration in minutes × RPE.
    """

    if elapsed is None or not _valid_rpe(rpe):

        return None

    if elapsed.total_seconds() <= 0:

        return None

    minutes = elapsed.total_seconds() / 60

    return minutes * rpe