"""
PerformanceLab

Elevation Presentation

Utilities for preparing workout elevation profiles.
"""

from math import asin, cos, radians, sin, sqrt

from performancelab import Workout

from .route import route_points


EARTH_RADIUS_METRES = 6_371_000.0


# ======================================================
# Distance between coordinates
# ======================================================

def _distance_between(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:

    """
    Returns the great-circle distance in metres.
    """

    lat_1 = radians(latitude_1)
    lon_1 = radians(longitude_1)

    lat_2 = radians(latitude_2)
    lon_2 = radians(longitude_2)

    delta_latitude = lat_2 - lat_1
    delta_longitude = lon_2 - lon_1

    value = (
        sin(delta_latitude / 2) ** 2
        + cos(lat_1)
        * cos(lat_2)
        * sin(delta_longitude / 2) ** 2
    )

    value = min(
        1.0,
        max(0.0, value),
    )

    return (
        2
        * EARTH_RADIUS_METRES
        * asin(sqrt(value))
    )


# ======================================================
# Elevation profile
# ======================================================

def elevation_profile(
    workout: Workout,
) -> list[dict]:

    """
    Returns a cumulative-distance elevation profile.

    Each item contains:

        distance_metres
        distance_km
        elevation
        latitude
        longitude
        time
    """

    points = route_points(workout)

    if not points:

        return []

    profile = []
    cumulative_distance = 0.0
    previous_point = None

    for point in points:

        elevation = point.get("elevation")

        if elevation is None:

            continue

        try:

            elevation_value = float(elevation)

        except (TypeError, ValueError):

            continue

        if previous_point is not None:

            cumulative_distance += _distance_between(
                previous_point["latitude"],
                previous_point["longitude"],
                point["latitude"],
                point["longitude"],
            )

        profile.append(
            {
                "distance_metres": cumulative_distance,
                "distance_km": (
                    cumulative_distance / 1000
                ),
                "elevation": elevation_value,
                "latitude": point["latitude"],
                "longitude": point["longitude"],
                "time": point.get("time"),
            }
        )

        previous_point = point

    return profile


# ======================================================
# Elevation values
# ======================================================

def elevation_values(
    workout: Workout,
) -> list[float]:

    return [
        point["elevation"]
        for point in elevation_profile(workout)
    ]


# ======================================================
# Minimum elevation
# ======================================================

def elevation_minimum(
    workout: Workout,
) -> float | None:

    values = elevation_values(workout)

    if not values:

        return None

    return min(values)


# ======================================================
# Maximum elevation
# ======================================================

def elevation_maximum(
    workout: Workout,
) -> float | None:

    values = elevation_values(workout)

    if not values:

        return None

    return max(values)


# ======================================================
# Elevation range
# ======================================================

def elevation_range(
    workout: Workout,
) -> float | None:

    minimum = elevation_minimum(workout)
    maximum = elevation_maximum(workout)

    if minimum is None or maximum is None:

        return None

    return maximum - minimum


# ======================================================
# Profile distance
# ======================================================

def elevation_profile_distance(
    workout: Workout,
) -> float:

    profile = elevation_profile(workout)

    if not profile:

        return 0.0

    return profile[-1]["distance_km"]


# ======================================================
# Availability
# ======================================================

def has_elevation_profile(
    workout: Workout,
) -> bool:

    return len(
        elevation_profile(workout)
    ) >= 2