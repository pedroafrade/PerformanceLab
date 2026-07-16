"""
PerformanceLab

Tests for elevation presentation utilities.
"""

import pytest

from performancelab import Workout

from performancelab.presentation import (
    elevation_maximum,
    elevation_minimum,
    elevation_profile,
    elevation_profile_distance,
    elevation_range,
    elevation_values,
    has_elevation_profile,
)


# ======================================================
# Helpers
# ======================================================

def create_workout_with_route():

    workout = Workout()

    workout.sensors.add(

        "gps",

        [
            {
                "latitude": 38.7200,
                "longitude": -9.1400,
                "elevation": 20,
                "time": (
                    "2026-07-01T08:00:00+00:00"
                ),
            },
            {
                "latitude": 38.7210,
                "longitude": -9.1390,
                "elevation": 35,
                "time": (
                    "2026-07-01T08:05:00+00:00"
                ),
            },
            {
                "latitude": 38.7220,
                "longitude": -9.1380,
                "elevation": 30,
                "time": (
                    "2026-07-01T08:10:00+00:00"
                ),
            },
        ],

    )

    return workout


# ======================================================
# Profile
# ======================================================

def test_elevation_profile():

    workout = create_workout_with_route()

    profile = elevation_profile(workout)

    assert len(profile) == 3

    assert profile[0]["distance_metres"] == 0.0

    assert profile[0]["distance_km"] == 0.0

    assert profile[0]["elevation"] == 20.0

    assert profile[1]["distance_metres"] > 0

    assert profile[2]["distance_metres"] > (
        profile[1]["distance_metres"]
    )

    assert profile[2]["distance_km"] == pytest.approx(
        profile[2]["distance_metres"] / 1000
    )


# ======================================================
# Values
# ======================================================

def test_elevation_values():

    workout = create_workout_with_route()

    assert elevation_values(workout) == [

        20.0,

        35.0,

        30.0,

    ]


# ======================================================
# Statistics
# ======================================================

def test_elevation_statistics():

    workout = create_workout_with_route()

    assert elevation_minimum(workout) == 20.0

    assert elevation_maximum(workout) == 35.0

    assert elevation_range(workout) == 15.0


# ======================================================
# Profile distance
# ======================================================

def test_elevation_profile_distance():

    workout = create_workout_with_route()

    distance = elevation_profile_distance(
        workout
    )

    assert distance > 0

    assert distance == pytest.approx(
        elevation_profile(workout)[-1][
            "distance_km"
        ]
    )


# ======================================================
# Availability
# ======================================================

def test_has_elevation_profile():

    workout = create_workout_with_route()

    assert has_elevation_profile(
        workout
    ) is True


# ======================================================
# Missing route
# ======================================================

def test_missing_route():

    workout = Workout()

    assert elevation_profile(workout) == []

    assert elevation_values(workout) == []

    assert elevation_minimum(workout) is None

    assert elevation_maximum(workout) is None

    assert elevation_range(workout) is None

    assert elevation_profile_distance(
        workout
    ) == 0.0

    assert has_elevation_profile(
        workout
    ) is False


# ======================================================
# Invalid elevation points
# ======================================================

def test_invalid_elevation_points_are_ignored():

    workout = Workout()

    workout.sensors.add(

        "gps",

        [
            {
                "latitude": 38.7200,
                "longitude": -9.1400,
                "elevation": None,
                "time": None,
            },
            {
                "latitude": 38.7210,
                "longitude": -9.1390,
                "elevation": "invalid",
                "time": None,
            },
            {
                "latitude": 38.7220,
                "longitude": -9.1380,
                "elevation": 40,
                "time": None,
            },
        ],

    )

    profile = elevation_profile(workout)

    assert len(profile) == 1

    assert profile[0]["elevation"] == 40.0

    assert profile[0]["distance_metres"] == 0.0

    assert has_elevation_profile(
        workout
    ) is False