"""
PerformanceLab

Route Presentation

Utilities for preparing GPS route data for user interfaces.
"""

from performancelab import Workout


# ======================================================
# Route points
# ======================================================

def route_points(
    workout: Workout,
) -> list[dict]:

    """
    Returns valid GPS points stored in the workout.

    Each returned item contains:

        latitude
        longitude
        elevation
        time
    """

    route = workout.sensors.get("gps")

    if not route:

        return []

    points = []

    for point in route:

        latitude = point.get("latitude")
        longitude = point.get("longitude")

        if latitude is None or longitude is None:

            continue

        points.append(

            {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "elevation": point.get(
                    "elevation"
                ),
                "time": point.get("time"),
            }

        )

    return points


# ======================================================
# Route coordinates
# ======================================================

def route_coordinates(
    workout: Workout,
) -> list[list[float]]:

    """
    Returns coordinates in PyDeck order:

        [longitude, latitude]
    """

    return [

        [
            point["longitude"],
            point["latitude"],
        ]

        for point in route_points(workout)

    ]


# ======================================================
# Route center
# ======================================================

def route_center(
    workout: Workout,
) -> tuple[float, float] | None:

    """
    Returns the average route latitude and longitude.
    """

    points = route_points(workout)

    if not points:

        return None

    latitude = sum(

        point["latitude"]

        for point in points

    ) / len(points)

    longitude = sum(

        point["longitude"]

        for point in points

    ) / len(points)

    return latitude, longitude


# ======================================================
# Has route
# ======================================================

def has_route(
    workout: Workout,
) -> bool:

    return len(route_points(workout)) >= 2