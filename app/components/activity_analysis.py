"""
PerformanceLab

Reusable completed-activity analysis.
"""

from datetime import datetime
from math import (
    asin,
    cos,
    radians,
    sin,
    sqrt,
)

import altair as alt
import streamlit as st

from performancelab.presentation import (
    route_points,
)

from .route_map import (
    show_route_map,
)


def _parse_time(
    value,
) -> datetime | None:

    if isinstance(
        value,
        datetime,
    ):
        return value

    if not value:
        return None

    try:
        return datetime.fromisoformat(
            str(value)
        )

    except ValueError:
        return None


def _elapsed_minutes(
    timestamp: datetime,
    start: datetime,
) -> float:

    return (
        timestamp - start
    ).total_seconds() / 60


def _haversine_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:
    """
    Distance between two GPS points in kilometres.
    """

    radius_km = 6371.0088

    lat_1 = radians(
        latitude_1
    )
    lat_2 = radians(
        latitude_2
    )

    delta_lat = radians(
        latitude_2 - latitude_1
    )

    delta_lon = radians(
        longitude_2 - longitude_1
    )

    value = (
        sin(
            delta_lat / 2
        ) ** 2
        + cos(lat_1)
        * cos(lat_2)
        * sin(
            delta_lon / 2
        ) ** 2
    )

    return (
        2
        * radius_km
        * asin(
            sqrt(value)
        )
    )


def _route_profile_rows(
    workout,
) -> list[dict]:
    """
    Builds elapsed-time elevation and pace samples
    from the GPS track.
    """

    points = route_points(
        workout
    )

    parsed = []

    for point in points:

        timestamp = _parse_time(
            point.get("time")
        )

        if timestamp is None:
            continue

        parsed.append(
            {
                **point,
                "timestamp": timestamp,
            }
        )

    if len(parsed) < 2:
        return []

    start = parsed[0][
        "timestamp"
    ]

    rows = []

    previous = None

    for point in parsed:

        pace = None

        if previous is not None:

            seconds = (
                point["timestamp"]
                - previous["timestamp"]
            ).total_seconds()

            distance = _haversine_km(
                previous["latitude"],
                previous["longitude"],
                point["latitude"],
                point["longitude"],
            )

            if (
                seconds > 0
                and distance > 0.002
            ):
                candidate = (
                    seconds
                    / 60
                    / distance
                )

                # Remove GPS spikes and stops.
                if (
                    1.5
                    <= candidate
                    <= 30
                ):
                    pace = candidate

        rows.append(
            {
                "Elapsed": (
                    _elapsed_minutes(
                        point["timestamp"],
                        start,
                    )
                ),
                "Elevation": (
                    float(
                        point["elevation"]
                    )
                    if point.get(
                        "elevation"
                    )
                    is not None
                    else None
                ),
                "Pace": pace,
            }
        )

        previous = point

    return rows


def _sensor_rows(
    workout,
    sensor_name: str,
) -> list[dict]:
    """
    Converts one sensor stream into elapsed-time rows.
    """

    samples = (
        workout.sensors.get(
            sensor_name
        )
        or []
    )

    parsed = []

    for sample in samples:

        timestamp = _parse_time(
            sample.get("time")
        )

        value = sample.get(
            "value"
        )

        if (
            timestamp is None
            or value is None
        ):
            continue

        try:
            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            continue

        parsed.append(
            (
                timestamp,
                numeric_value,
            )
        )

    if not parsed:
        return []

    start = parsed[0][0]

    return [
        {
            "Elapsed": (
                _elapsed_minutes(
                    timestamp,
                    start,
                )
            ),
            "Value": value,
        }
        for timestamp, value
        in parsed
    ]


def _available_metrics(
    workout,
) -> dict[str, str]:

    metrics = {}

    if workout.sensors.get(
        "heart_rate"
    ):
        metrics[
            "Heart rate"
        ] = "heart_rate"

    if workout.sensors.get(
        "power"
    ):
        metrics[
            "Power"
        ] = "power"

    if workout.sensors.get(
        "cadence"
    ):
        metrics[
            "Cadence"
        ] = "cadence"

    profile = (
        _route_profile_rows(
            workout
        )
    )

    if any(
        row["Pace"] is not None
        for row in profile
    ):
        metrics[
            "Pace"
        ] = "pace"

    return metrics


def _metric_axis(
    metric: str,
) -> tuple[str, str]:

    return {
        "Heart rate": (
            "Heart rate",
            "bpm",
        ),
        "Power": (
            "Power",
            "W",
        ),
        "Cadence": (
            "Cadence",
            "spm",
        ),
        "Pace": (
            "Pace",
            "min/km",
        ),
    }[metric]


def _metric_rows(
    workout,
    metric: str,
) -> list[dict]:

    if metric == "Pace":

        return [
            {
                "Elapsed": (
                    row["Elapsed"]
                ),
                "Value": (
                    row["Pace"]
                ),
            }
            for row in (
                _route_profile_rows(
                    workout
                )
            )
            if row["Pace"]
            is not None
        ]

    sensor_name = (
        _available_metrics(
            workout
        )[metric]
    )

    return _sensor_rows(
        workout,
        sensor_name,
    )


def _activity_profile_chart(
    workout,
    *,
    metric: str,
):
    """
    One selected physiological/performance metric
    over an elevation backdrop.
    """

    profile_rows = (
        _route_profile_rows(
            workout
        )
    )

    metric_rows = (
        _metric_rows(
            workout,
            metric,
        )
    )

    if not metric_rows:
        return None

    title, unit = (
        _metric_axis(
            metric
        )
    )

    layers = []

    elevation_rows = [
        row
        for row in profile_rows
        if row["Elevation"]
        is not None
    ]

    if elevation_rows:

        elevation = (
            alt.Chart(
                alt.Data(
                    values=elevation_rows
                )
            )
            .mark_area(
                opacity=0.30,
            )
            .encode(
                x=alt.X(
                    "Elapsed:Q",
                    title="Elapsed time (min)",
                ),
                y=alt.Y(
                    "Elevation:Q",
                    title=None,
                    axis=None,
                    scale=alt.Scale(
                        zero=False
                    ),
                ),
                tooltip=[
                    alt.Tooltip(
                        "Elapsed:Q",
                        title="Elapsed",
                        format=".1f",
                    ),
                    alt.Tooltip(
                        "Elevation:Q",
                        title="Elevation (m)",
                        format=".0f",
                    ),
                ],
            )
        )

        layers.append(
            elevation
        )

    metric_line = (
        alt.Chart(
            alt.Data(
                values=metric_rows
            )
        )
        .mark_line(
            strokeWidth=1.8,
        )
        .encode(
            x=alt.X(
                "Elapsed:Q",
                title="Elapsed time (min)",
            ),
            y=alt.Y(
                "Value:Q",
                title=(
                    f"{title} ({unit})"
                ),
                scale=alt.Scale(
                    zero=False
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Elapsed:Q",
                    title="Elapsed",
                    format=".1f",
                ),
                alt.Tooltip(
                    "Value:Q",
                    title=title,
                    format=".1f",
                ),
            ],
        )
    )

    layers.append(
        metric_line
    )

    return (
        alt.layer(
            *layers
        )
        .resolve_scale(
            y="independent"
        )
        .properties(
            height=235
        )
    )


def _environment_label(
    value,
    *,
    suffix: str,
) -> str:

    if value is None:
        return "—"

    try:
        numeric = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return "—"

    return (
        f"{numeric:.0f}{suffix}"
    )


def show_activity_analysis(
    workout,
) -> None:
    """
    Shows route, environment and sensor analysis
    for one completed workout.
    """

    if workout is None:
        return

    with st.container(
        border=True
    ):
        st.markdown(
            "**Activity analysis**"
        )

        (
            temperature_column,
            humidity_column,
            terrain_column,
        ) = st.columns(
            3,
            gap="small",
        )

        with temperature_column:
            st.metric(
                "Air temperature",
                _environment_label(
                    workout
                    .environment
                    .temperature,
                    suffix=" °C",
                ),
            )

        with humidity_column:
            st.metric(
                "Humidity",
                _environment_label(
                    workout
                    .environment
                    .humidity,
                    suffix="%",
                ),
            )

        with terrain_column:
            st.metric(
                "Terrain",
                (
                    workout
                    .environment
                    .terrain
                    or "—"
                ),
            )

        if workout.sensors.get(
            "gps"
        ):
            st.markdown(
                "**Route**"
            )

            show_route_map(
                workout
            )

        metrics = (
            _available_metrics(
                workout
            )
        )

        if not metrics:
            return

        st.markdown(
            "**Performance profile**"
        )

        metric = st.selectbox(
            "Metric",
            options=tuple(
                metrics.keys()
            ),
            key=(
                "today_activity_"
                "analysis_metric"
            ),
        )

        chart = (
            _activity_profile_chart(
                workout,
                metric=metric,
            )
        )

        if chart is not None:

            st.altair_chart(
                chart,
                use_container_width=True,
            )

        st.caption(
            "Elevation is shown as the "
            "background profile."
        )