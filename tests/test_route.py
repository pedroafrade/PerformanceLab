"""
PerformanceLab

Tests for route presentation utilities.
"""

from performancelab import Workout
from performancelab.presentation import (
    has_route,
    route_center,
    route_coordinates,
    route_points,
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
                "time": "2026-07-01T08:00:00+00:00",
            },
            {
                "latitude": 38.7220,
                "longitude": -9.1380,
                "elevation": 25,
                "time": "2026-07-01T08:05:00+00:00",
            },
            {
                "latitude": 38.7240,
                "longitude": -9.1360,
                "elevation": 30,
                "time": "2026-07-01T08:10:00+00:00",
            },
        ],

    )

    return workout


# ======================================================

def test_route_points():

    workout = create_workout_with_route()

    points = route_points(workout)

    assert len(points) == 3

    assert points[0]["latitude"] == 38.7200

    assert points[0]["longitude"] == -9.1400


# ======================================================

def test_route_coordinates():

    workout = create_workout_with_route()

    coordinates = route_coordinates(workout)

    assert coordinates == [

        [-9.1400, 38.7200],

        [-9.1380, 38.7220],

        [-9.1360, 38.7240],

    ]


# ======================================================

def test_route_center():

    workout = create_workout_with_route()

    center = route_center(workout)

    assert center is not None

    latitude, longitude = center

    assert latitude == 38.7220

    assert longitude == -9.1380


# ======================================================

def test_has_route():

    workout = create_workout_with_route()

    assert has_route(workout) is True


# ======================================================

def test_empty_route():

    workout = Workout()

    assert route_points(workout) == []

    assert route_coordinates(workout) == []

    assert route_center(workout) is None

    assert has_route(workout) is False


# ======================================================

def test_invalid_points_are_ignored():

    workout = Workout()

    workout.sensors.add(

        "gps",

        [
            {
                "latitude": None,
                "longitude": -9.14,
            },
            {
                "latitude": 38.72,
                "longitude": None,
            },
            {
                "latitude": 38.73,
                "longitude": -9.13,
            },
        ],

    )

    points = route_points(workout)

    assert len(points) == 1

    assert points[0]["latitude"] == 38.73