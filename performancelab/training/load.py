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
ELEVATION_GAIN_BLOCK_METRES = 100.0
ELEVATION_LOAD_PER_BLOCK = 0.05
MAX_ELEVATION_LOAD_BONUS = 0.30
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

def planned_elevation_load_factor(
    workout,
) -> float:
    """
    Returns a conservative elevation load multiplier for
    planned running workouts.

    Each 100 metres of elevation gain adds 5%, capped at
    a maximum elevation bonus of 30%.
    """

    sport = str(
        getattr(
            workout,
            "sport",
            "",
        )
        or ""
    ).strip().lower()

    is_running = any(
        token in sport
        for token in (
            "run",
            "running",
            "trail",
            "jog",
        )
    )

    if not is_running:
        return 1.0

    elevation_gain = getattr(
        workout,
        "elevation_gain",
        None,
    )

    if (
        not isinstance(
            elevation_gain,
            (int, float),
        )
        or isinstance(
            elevation_gain,
            bool,
        )
        or elevation_gain <= 0
    ):
        return 1.0

    elevation_bonus = min(
        (
            elevation_gain
            / ELEVATION_GAIN_BLOCK_METRES
        )
        * ELEVATION_LOAD_PER_BLOCK,
        MAX_ELEVATION_LOAD_BONUS,
    )

    return 1.0 + elevation_bonus

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

    base_load = minutes * rpe

    return (
        base_load
        * planned_elevation_load_factor(
            workout
        )
    )

# ======================================================
# Planned weekly load
# ======================================================

def planned_weekly_load(
    workouts,
) -> float:
    """
    Returns the estimated total load of a collection of
    planned workouts.

    Workouts without enough information to estimate load
    are ignored.
    """

    total = 0.0

    for workout in workouts:

        load = planned_workout_load(
            workout
        )

        if load is not None:
            total += load

    return total
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