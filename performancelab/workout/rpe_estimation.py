"""
PerformanceLab

Workout exertion estimation.

Applies physiological exertion estimates to workout data.
"""

from performancelab.physiology import (
    estimate_rpe_from_heart_rate,
)

from .model import Workout

MINUTES_PER_DURATION_RPE_POINT = 30.0
MAX_DURATION_RPE_BONUS = 3.0
MAX_RPE = 10.0


def _duration_rpe_bonus(
    duration,
) -> float:
    """
    Returns additional exertion caused by workout duration.
    """

    if duration is None:
        return 0.0

    duration_minutes = max(
        0.0,
        duration.total_seconds() / 60,
    )

    return min(
        MAX_DURATION_RPE_BONUS,
        duration_minutes
        / MINUTES_PER_DURATION_RPE_POINT,
    )

def estimate_workout_rpe(
    workout: Workout,
    *,
    max_hr: float | None,
    resting_hr: float | None,
) -> float | None:
    """
    Estimates and stores workout RPE from heart-rate samples.

    Manual RPE is preserved and continues to take priority through
    AthleteFeedback.effective_rpe.
    """

    if not isinstance(
        workout,
        Workout,
    ):
        raise TypeError(
            "workout must be a Workout"
        )

    heart_rate_sensor = workout.sensors.get(
        "heart_rate"
    )

    heart_rates = [
        sample.get("value")
        for sample in (
            heart_rate_sensor or ()
        )
        if isinstance(
            sample,
            dict,
        )
    ]

    intensity_estimate = estimate_rpe_from_heart_rate(
        heart_rates,
        max_hr=max_hr,
        resting_hr=resting_hr,
    )

    if intensity_estimate is None:
        estimate = None

    else:
        estimate = round(
            min(
                MAX_RPE,
                intensity_estimate
                + _duration_rpe_bonus(
                    workout.duration
                ),
            ),
            1,
        )

    workout.feedback.estimated_rpe = estimate

    return estimate