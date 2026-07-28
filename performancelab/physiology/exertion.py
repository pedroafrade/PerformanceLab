"""
PerformanceLab

Estimated workout exertion.

Provides a conservative heart-rate-based RPE estimate.
The result is a heuristic and may be overridden by the athlete.
"""

from collections.abc import Iterable

from .heartrate import percent_hrr


def _rpe_from_percent_hrr(
    percentage: float,
) -> float:
    """
    Converts heart-rate-reserve intensity into estimated RPE.
    """

    if percentage < 50:
        return 2.0

    if percentage < 60:
        return 3.0

    if percentage < 70:
        return 4.0

    if percentage < 80:
        return 5.0

    if percentage < 90:
        return 7.0

    return 9.0


def estimate_rpe_from_heart_rate(
    heart_rates: Iterable[float | None],
    *,
    max_hr: float | None,
    resting_hr: float | None,
) -> float | None:
    """
    Estimates workout RPE from recorded heart-rate samples.

    The estimate uses relative heart-rate reserve so that the same
    heart rate may represent different effort for different athletes.
    """

    estimated_values = []

    for heart_rate in heart_rates:

        percentage = percent_hrr(
            heart_rate,
            max_hr,
            resting_hr,
        )

        if percentage is None:
            continue

        percentage = max(
            0.0,
            min(
                percentage,
                100.0,
            ),
        )

        estimated_values.append(
            _rpe_from_percent_hrr(
                percentage
            )
        )

    if not estimated_values:
        return None

    return round(
        sum(estimated_values)
        / len(estimated_values),
        1,
    )