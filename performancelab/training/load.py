"""
PerformanceLab

Training Load

Utilities for calculating training load.
"""

PLANNED_INTENSITY_RPE = {
    "none": 0.0,
    "very easy": 2.0,
    "easy": 3.0,
    "easy to moderate": 4.0,
    "moderately hard": 6.0,
    "hard": 7.0,
    "very hard": 9.0,
    "race effort": 8.0,
}

# ======================================================
# Workout load (Session RPE)
# ======================================================

def workout_load(workout):

    duration = workout.duration
    rpe = workout.feedback.effective_rpe

    if duration is None:

        return None

    if rpe is None:

        return None

    minutes = duration.total_seconds() / 60

    return minutes * rpe

# ======================================================
# Planned workout load
# ======================================================

def planned_workout_rpe(
    workout,
) -> float | None:
    """
    Returns the estimated RPE represented by a planned
    workout's semantic intensity.
    """

    intensity = getattr(
        workout,
        "intensity",
        None,
    )

    if not isinstance(
        intensity,
        str,
    ):
        return None

    normalized_intensity = (
        intensity.strip().lower()
    )

    if not normalized_intensity:
        return None

    return PLANNED_INTENSITY_RPE.get(
        normalized_intensity
    )


# ======================================================

def planned_workout_load(
    workout,
) -> float | None:
    """
    Estimates session-RPE load for a planned workout.

    Planned workouts use their semantic intensity because
    athlete feedback does not exist before completion.
    """

    duration = getattr(
        workout,
        "duration",
        None,
    )

    if duration is None:
        return None

    rpe = planned_workout_rpe(
        workout
    )

    if rpe is None:
        return None

    minutes = (
        duration.total_seconds()
        / 60
    )

    return minutes * rpe
# ======================================================
# Weekly load
# ======================================================

def weekly_load(week):

    total = 0.0

    for workout in week.history:

        value = workout_load(workout)

        if value is not None:

            total += value

    return total


# ======================================================
# Monthly load
# ======================================================

def monthly_load(month):

    return sum(

        weekly_load(week)

        for week in month.weeks

    )