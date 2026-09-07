"""
PerformanceLab

Metric-based completed workout stimulus classification.
"""

from datetime import datetime

from .workout_stimulus import (
    WorkoutStimulus,
)


MINIMUM_VALID_SAMPLES = 120
MAXIMUM_SAMPLE_GAP_SECONDS = 30.0

LT2_MINIMUM_BLOCK_SECONDS = 4 * 60
LT2_MAXIMUM_BLOCK_SECONDS = 15 * 60
LT2_MINIMUM_TOTAL_SECONDS = 12 * 60

TEMPO_MINIMUM_SECONDS = 18 * 60

VO2_MINIMUM_BLOCK_SECONDS = 60
VO2_MAXIMUM_BLOCK_SECONDS = 5 * 60
VO2_MINIMUM_TOTAL_SECONDS = 6 * 60

HILL_MINIMUM_ELEVATION_PER_KM = 30.0
LONG_RUN_MINIMUM_SECONDS = 90 * 60


def _timestamp(value):

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):

        try:
            return datetime.fromisoformat(
                value.replace(
                    "Z",
                    "+00:00",
                )
            )

        except ValueError:
            return None

    return None


def _heart_rate_samples(
    workout,
) -> tuple[tuple[datetime, float], ...]:

    sensor = workout.sensors.get(
        "heart_rate"
    )

    if not isinstance(
        sensor,
        (list, tuple),
    ):
        return ()

    samples = []

    for item in sensor:

        if not isinstance(item, dict):
            continue

        timestamp = _timestamp(
            item.get("time")
        )

        value = item.get("value")

        if (
            timestamp is None
            or not isinstance(
                value,
                (int, float),
            )
            or isinstance(value, bool)
            or value <= 0
        ):
            continue

        samples.append(
            (
                timestamp,
                float(value),
            )
        )

    samples.sort(
        key=lambda sample: sample[0]
    )

    return tuple(samples)


def _effort_blocks(
    samples,
    *,
    minimum_heart_rate: float,
) -> tuple[float, ...]:
    """
    Returns durations of sustained effort blocks.

    Short recording gaps are tolerated. A drop below the
    selected intensity separates two effort blocks.
    """

    blocks = []
    block_start = None
    previous_time = None

    for timestamp, heart_rate in samples:

        if (
            previous_time is not None
            and (
                timestamp - previous_time
            ).total_seconds()
            > MAXIMUM_SAMPLE_GAP_SECONDS
        ):
            if block_start is not None:
                blocks.append(
                    (
                        previous_time
                        - block_start
                    ).total_seconds()
                )
                block_start = None

        if heart_rate >= minimum_heart_rate:

            if block_start is None:
                block_start = timestamp

        elif block_start is not None:

            blocks.append(
                (
                    previous_time
                    - block_start
                ).total_seconds()
            )

            block_start = None

        previous_time = timestamp

    if (
        block_start is not None
        and previous_time is not None
    ):
        blocks.append(
            (
                previous_time
                - block_start
            ).total_seconds()
        )

    return tuple(
        duration
        for duration in blocks
        if duration > 0
    )


def _elevation_density(
    workout,
) -> float:

    distance = getattr(
        workout,
        "distance",
        None,
    )

    elevation_gain = getattr(
        workout,
        "elevation_gain",
        None,
    )

    if (
        not isinstance(
            distance,
            (int, float),
        )
        or distance <= 0
        or not isinstance(
            elevation_gain,
            (int, float),
        )
        or elevation_gain < 0
    ):
        return 0.0

    return elevation_gain / distance


def metric_workout_stimulus(
    workout,
    *,
    heart_rate_profile,
) -> WorkoutStimulus:
    """
    Infers the dominant completed stimulus from recorded
    metrics and the athlete's individual heart-rate profile.

    UNKNOWN is returned whenever evidence is insufficient.
    """

    if (
        workout is None
        or heart_rate_profile is None
    ):
        return WorkoutStimulus.UNKNOWN

    samples = _heart_rate_samples(
        workout
    )

    if len(samples) < MINIMUM_VALID_SAMPLES:
        return WorkoutStimulus.UNKNOWN

    threshold_hr = getattr(
        heart_rate_profile,
        "threshold_hr",
        None,
    )

    max_hr = getattr(
        heart_rate_profile,
        "max_hr",
        None,
    )

    duration = getattr(
        workout,
        "duration",
        None,
    )

    duration_seconds = (
        duration.total_seconds()
        if duration is not None
        else 0.0
    )

    # VO2max and short hill repetitions.
    if (
        isinstance(max_hr, (int, float))
        and max_hr > 0
    ):

        vo2_blocks = _effort_blocks(
            samples,
            minimum_heart_rate=(
                max_hr * 0.90
            ),
        )

        valid_vo2_blocks = tuple(
            block
            for block in vo2_blocks
            if (
                VO2_MINIMUM_BLOCK_SECONDS
                <= block
                <= VO2_MAXIMUM_BLOCK_SECONDS
            )
        )

        if (
            len(valid_vo2_blocks) >= 3
            and sum(valid_vo2_blocks)
            >= VO2_MINIMUM_TOTAL_SECONDS
        ):

            if (
                _elevation_density(workout)
                >= HILL_MINIMUM_ELEVATION_PER_KM
            ):
                return WorkoutStimulus.HILLS

            return WorkoutStimulus.VO2MAX

    if (
        isinstance(
            threshold_hr,
            (int, float),
        )
        and threshold_hr > 0
    ):

        threshold_blocks = _effort_blocks(
            samples,
            minimum_heart_rate=(
                threshold_hr * 0.95
            ),
        )

        valid_lt2_blocks = tuple(
            block
            for block in threshold_blocks
            if (
                LT2_MINIMUM_BLOCK_SECONDS
                <= block
                <= LT2_MAXIMUM_BLOCK_SECONDS
            )
        )

        # Includes patterns such as 2×10, 3×8, 4×6,
        # 4×8 and other equivalent threshold sessions.
        if (
            len(valid_lt2_blocks) >= 2
            and sum(valid_lt2_blocks)
            >= LT2_MINIMUM_TOTAL_SECONDS
        ):
            return WorkoutStimulus.THRESHOLD

        if any(
            block >= TEMPO_MINIMUM_SECONDS
            for block in threshold_blocks
        ):
            return WorkoutStimulus.TEMPO

        high_intensity_seconds = sum(
            threshold_blocks
        )

        high_intensity_fraction = (
            high_intensity_seconds
            / duration_seconds
            if duration_seconds > 0
            else 0.0
        )

        if (
            duration_seconds
            >= LONG_RUN_MINIMUM_SECONDS
            and high_intensity_fraction
            < 0.25
        ):
            return WorkoutStimulus.LONG

        if (
            duration_seconds >= 20 * 60
            and high_intensity_fraction
            < 0.10
        ):
            return WorkoutStimulus.EASY

    return WorkoutStimulus.UNKNOWN