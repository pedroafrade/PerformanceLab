"""
PerformanceLab

Presentation package.
"""

from .card import (
    SensorCard,
    cadence_card,
    heart_rate_card,
    power_card,
    sensor_card,
)

from .chart import (
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

from .dashboard import DashboardData

from .elevation import (
    elevation_maximum,
    elevation_minimum,
    elevation_profile,
    elevation_profile_distance,
    elevation_range,
    elevation_values,
    has_elevation_profile,
)

from .route import (
    has_route,
    route_center,
    route_coordinates,
    route_points,
)


__all__ = [

    # Dashboard
    "DashboardData",

    # Route
    "has_route",
    "route_center",
    "route_coordinates",
    "route_points",

    # Elevation
    "elevation_profile",
    "elevation_values",
    "elevation_minimum",
    "elevation_maximum",
    "elevation_range",
    "elevation_profile_distance",
    "has_elevation_profile",

    # Generic chart data
    "sensor_series",
    "sensor_values",
    "sensor_average",
    "sensor_minimum",
    "sensor_maximum",
    "sensor_summary",
    "has_sensor_series",

    # Heart rate
    "heart_rate_series",
    "heart_rate_summary",

    # Power
    "power_series",
    "power_summary",

    # Cadence
    "cadence_series",
    "cadence_summary",

    # Sensor cards
    "SensorCard",
    "sensor_card",
    "heart_rate_card",
    "power_card",
    "cadence_card",

]