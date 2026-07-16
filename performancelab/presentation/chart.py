"""
PerformanceLab

Chart Presentation

Utilities for preparing workout sensor data for charts.
"""

from datetime import datetime

from performancelab import Workout


# ======================================================
# Timestamp normalization
# ======================================================

def _timestamp(value):

    if value is None:

        return None

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


# ======================================================
# Generic sensor series
# ======================================================

def sensor_series(
    workout: Workout,
    sensor_name: str,
) -> list[dict]:

    """
    Returns valid samples for a workout sensor.

    Expected sensor format:

        [
            {
                "time": "2026-07-01T08:00:00+00:00",
                "value": 145,
            },
            ...
        ]

    Returned samples contain:

        time
        value
        elapsed_seconds
    """

    sensor = workout.sensors.get(
        sensor_name
    )

    if not isinstance(sensor, list):

        return []

    samples = []

    for item in sensor:

        if not isinstance(item, dict):

            continue

        value = item.get("value")

        if value is None:

            continue

        try:

            numeric_value = float(value)

        except (TypeError, ValueError):

            continue

        samples.append(

            {
                "time": _timestamp(
                    item.get("time")
                ),
                "value": numeric_value,
            }

        )

    if not samples:

        return []

    dated_samples = [

        sample

        for sample in samples

        if sample["time"] is not None

    ]

    undated_samples = [

        sample

        for sample in samples

        if sample["time"] is None

    ]

    dated_samples.sort(

        key=lambda sample: sample["time"]

    )

    samples = dated_samples + undated_samples

    start_time = next(

        (
            sample["time"]

            for sample in samples

            if sample["time"] is not None
        ),

        None,

    )

    result = []

    for index, sample in enumerate(samples):

        sample_time = sample["time"]

        if (

            start_time is not None

            and sample_time is not None

        ):

            elapsed_seconds = (

                sample_time - start_time

            ).total_seconds()

        else:

            elapsed_seconds = float(index)

        result.append(

            {
                "time": sample_time,
                "value": sample["value"],
                "elapsed_seconds": (
                    elapsed_seconds
                ),
            }

        )

    return result


# ======================================================
# Generic sensor values
# ======================================================

def sensor_values(
    workout: Workout,
    sensor_name: str,
) -> list[float]:

    return [

        sample["value"]

        for sample in sensor_series(
            workout,
            sensor_name,
        )

    ]


# ======================================================
# Generic sensor statistics
# ======================================================

def sensor_average(
    workout: Workout,
    sensor_name: str,
) -> float | None:

    values = sensor_values(

        workout,

        sensor_name,

    )

    if not values:

        return None

    return sum(values) / len(values)


# ======================================================

def sensor_minimum(
    workout: Workout,
    sensor_name: str,
) -> float | None:

    values = sensor_values(

        workout,

        sensor_name,

    )

    if not values:

        return None

    return min(values)


# ======================================================

def sensor_maximum(
    workout: Workout,
    sensor_name: str,
) -> float | None:

    values = sensor_values(

        workout,

        sensor_name,

    )

    if not values:

        return None

    return max(values)


# ======================================================

def sensor_summary(
    workout: Workout,
    sensor_name: str,
) -> dict:

    values = sensor_values(

        workout,

        sensor_name,

    )

    if not values:

        return {

            "samples": 0,

            "average": None,

            "minimum": None,

            "maximum": None,

        }

    return {

        "samples": len(values),

        "average": sum(values) / len(values),

        "minimum": min(values),

        "maximum": max(values),

    }


# ======================================================
# Heart rate
# ======================================================

def heart_rate_series(
    workout: Workout,
) -> list[dict]:

    return sensor_series(

        workout,

        "heart_rate",

    )


# ======================================================

def heart_rate_summary(
    workout: Workout,
) -> dict:

    return sensor_summary(

        workout,

        "heart_rate",

    )


# ======================================================
# Power
# ======================================================

def power_series(
    workout: Workout,
) -> list[dict]:

    return sensor_series(

        workout,

        "power",

    )


# ======================================================

def power_summary(
    workout: Workout,
) -> dict:

    return sensor_summary(

        workout,

        "power",

    )


# ======================================================
# Cadence
# ======================================================

def cadence_series(
    workout: Workout,
) -> list[dict]:

    return sensor_series(

        workout,

        "cadence",

    )


# ======================================================

def cadence_summary(
    workout: Workout,
) -> dict:

    return sensor_summary(

        workout,

        "cadence",

    )


# ======================================================
# Sensor availability
# ======================================================

def has_sensor_series(
    workout: Workout,
    sensor_name: str,
) -> bool:

    return bool(

        sensor_series(
            workout,
            sensor_name,
        )

    )