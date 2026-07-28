"""
PerformanceLab

Workout exertion estimation.

Applies physiological exertion estimates to workout data.
"""

from performancelab.physiology import (
    estimate_rpe_from_heart_rate,
)

from .model import Workout


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

    estimate = estimate_rpe_from_heart_rate(
        heart_rates,
        max_hr=max_hr,
        resting_hr=resting_hr,
    )

    workout.feedback.estimated_rpe = estimate

    return estimate