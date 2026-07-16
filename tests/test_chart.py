"""
PerformanceLab

Tests for chart presentation utilities.
"""

from datetime import datetime, timezone

from performancelab import Workout

from performancelab.presentation import (
    cadence_series,
    cadence_summary,
    has_sensor_series,
    heart_rate_series,
    heart_rate_summary,
    power_series,
    power_summary,
    sensor_average,
    sensor_maximum,
    sensor_minimum,
    sensor_series,
    sensor_summary,
    sensor_values,
)


# ======================================================
# Helpers
# ======================================================

def create_workout_with_sensors():

    workout = Workout()

    workout.sensors.add(

        "heart_rate",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 140,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 150,
            },
            {
                "time": (
                    "2026-07-01T08:02:00+00:00"
                ),
                "value": 160,
            },
        ],

    )

    workout.sensors.add(

        "power",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 200,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 250,
            },
        ],

    )

    workout.sensors.add(

        "cadence",

        [
            {
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
                "value": 80,
            },
            {
                "time": (
                    "2026-07-01T08:01:00+00:00"
                ),
                "value": 90,
            },
        ],

    )

    return workout


# ======================================================
# Generic series
# ======================================================

def test_sensor_series():

    workout = create_workout_with_sensors()

    series = sensor_series(

        workout,

        "heart_rate",

    )

    assert len(series) == 3

    assert series[0]["value"] == 140

    assert series[0]["time"] == datetime(

        2026,

        7,

        1,

        8,

        0,

        tzinfo=timezone.utc,

    )

    assert series[0]["elapsed_seconds"] == 0

    assert series[1]["elapsed_seconds"] == 60

    assert series[2]["elapsed_seconds"] == 120


# ======================================================
# Values
# ======================================================

def test_sensor_values():

    workout = create_workout_with_sensors()

    assert sensor_values(

        workout,

        "heart_rate",

    ) == [

        140,

        150,

        160,

    ]


# ======================================================
# Statistics
# ======================================================

def test_sensor_statistics():

    workout = create_workout_with_sensors()

    assert sensor_average(

        workout,

        "heart_rate",

    ) == 150

    assert sensor_minimum(

        workout,

        "heart_rate",

    ) == 140

    assert sensor_maximum(

        workout,

        "heart_rate",

    ) == 160


# ======================================================

def test_sensor_summary():

    workout = create_workout_with_sensors()

    summary = sensor_summary(

        workout,

        "heart_rate",

    )

    assert summary == {

        "samples": 3,

        "average": 150,

        "minimum": 140,

        "maximum": 160,

    }


# ======================================================
# Heart rate
# ======================================================

def test_heart_rate_data():

    workout = create_workout_with_sensors()

    assert len(

        heart_rate_series(workout)

    ) == 3

    assert heart_rate_summary(

        workout

    )["maximum"] == 160


# ======================================================
# Power
# ======================================================

def test_power_data():

    workout = create_workout_with_sensors()

    assert [

        sample["value"]

        for sample in power_series(workout)

    ] == [

        200,

        250,

    ]

    assert power_summary(

        workout

    )["average"] == 225


# ======================================================
# Cadence
# ======================================================

def test_cadence_data():

    workout = create_workout_with_sensors()

    assert [

        sample["value"]

        for sample in cadence_series(workout)

    ] == [

        80,

        90,

    ]

    assert cadence_summary(

        workout

    )["maximum"] == 90


# ======================================================
# Sensor availability
# ======================================================

def test_has_sensor_series():

    workout = create_workout_with_sensors()

    assert has_sensor_series(

        workout,

        "heart_rate",

    ) is True

    assert has_sensor_series(

        workout,

        "temperature",

    ) is False


# ======================================================
# Missing sensor
# ======================================================

def test_missing_sensor():

    workout = Workout()

    assert sensor_series(

        workout,

        "heart_rate",

    ) == []

    assert sensor_values(

        workout,

        "heart_rate",

    ) == []

    assert sensor_average(

        workout,

        "heart_rate",

    ) is None

    assert sensor_minimum(

        workout,

        "heart_rate",

    ) is None

    assert sensor_maximum(

        workout,

        "heart_rate",

    ) is None

    assert sensor_summary(

        workout,

        "heart_rate",

    ) == {

        "samples": 0,

        "average": None,

        "minimum": None,

        "maximum": None,

    }


# ======================================================
# Invalid samples
# ======================================================

def test_invalid_samples_are_ignored():

    workout = Workout()

    workout.sensors.add(

        "heart_rate",

        [
            {
                "time": None,
                "value": None,
            },
            {
                "time": "invalid time",
                "value": "invalid value",
            },
            {
                "time": None,
                "value": 145,
            },
        ],

    )

    series = heart_rate_series(workout)

    assert len(series) == 1

    assert series[0]["value"] == 145

    assert series[0]["time"] is None

    assert series[0]["elapsed_seconds"] == 0