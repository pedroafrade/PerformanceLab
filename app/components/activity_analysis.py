"""
PerformanceLab

Reusable completed-activity analysis.
"""

from bisect import bisect_left
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


def _workout_datetime(
    workout,
) -> datetime | None:

    value = getattr(
        workout,
        "date",
        None,
    )

    if isinstance(
        value,
        datetime,
    ):
        return value

    if value is None:
        return None

    return datetime.combine(
        value,
        datetime.min.time(),
    )


def _haversine_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float,
) -> float:

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
    Builds cumulative route distance, progress,
    elevation and instantaneous pace.
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
                "Timestamp": timestamp,
                "Latitude": float(
                    point["latitude"]
                ),
                "Longitude": float(
                    point["longitude"]
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
            }
        )

    if len(parsed) < 2:
        return []

    cumulative_distance = 0.0
    rows = []

    previous = None

    for point in parsed:

        pace = None

        if previous is not None:

            segment_distance = (
                _haversine_km(
                    previous["Latitude"],
                    previous["Longitude"],
                    point["Latitude"],
                    point["Longitude"],
                )
            )

            seconds = (
                point["Timestamp"]
                - previous["Timestamp"]
            ).total_seconds()

            cumulative_distance += (
                segment_distance
            )

            if (
                seconds > 0
                and segment_distance
                > 0.002
            ):
                candidate = (
                    seconds
                    / 60
                    / segment_distance
                )

                if (
                    1.5
                    <= candidate
                    <= 30
                ):
                    pace = candidate

        rows.append(
            {
                **point,
                "Distance": (
                    cumulative_distance
                ),
                "Pace": pace,
            }
        )

        previous = point

    total_distance = (
        rows[-1]["Distance"]
    )

    if total_distance <= 0:
        return []

    return [
        {
            **row,
            "Progress": (
                row["Distance"]
                / total_distance
                * 100
            ),
        }
        for row in rows
    ]


def _resample_route(
    workout,
    *,
    points: int = 50,
) -> list[dict]:
    """
    Normalises a route to a fixed number of positions.
    """

    route = (
        _route_profile_rows(
            workout
        )
    )

    if len(route) < 2:
        return []

    result = []
    index = 0

    for target_index in range(
        points
    ):

        target = (
            target_index
            / (points - 1)
            * 100
        )

        while (
            index < len(route) - 1
            and abs(
                route[index + 1][
                    "Progress"
                ]
                - target
            )
            < abs(
                route[index][
                    "Progress"
                ]
                - target
            )
        ):
            index += 1

        result.append(
            route[index]
        )

    return result


def _route_similarity_score(
    workout,
    candidate,
) -> float:
    """
    Returns a 0–100 geographical route similarity.

    Geometry has more weight than total distance and
    reverse-direction traversals are supported.
    """

    current = _resample_route(
        workout
    )
    previous = _resample_route(
        candidate
    )

    if (
        not current
        or not previous
    ):
        return 0.0

    current_length = (
        current[-1]["Distance"]
    )
    previous_length = (
        previous[-1]["Distance"]
    )

    largest = max(
        current_length,
        previous_length,
    )

    if largest <= 0:
        return 0.0

    length_similarity = max(
        0.0,
        1.0
        - (
            abs(
                current_length
                - previous_length
            )
            / largest
        ),
    )

    if length_similarity < 0.72:
        return 0.0

    def mean_geometry_distance(
        second_route,
    ) -> float:

        distances = [
            _haversine_km(
                first["Latitude"],
                first["Longitude"],
                second["Latitude"],
                second["Longitude"],
            )
            for first, second
            in zip(
                current,
                second_route,
            )
        ]

        return (
            sum(distances)
            / len(distances)
        )

    forward_distance = (
        mean_geometry_distance(
            previous
        )
    )

    reverse_distance = (
        mean_geometry_distance(
            list(
                reversed(
                    previous
                )
            )
        )
    )

    geometry_distance = min(
        forward_distance,
        reverse_distance,
    )

    # Routes that are geographically too far apart
    # cannot be considered the same route, even when
    # their total distance is very similar.
    if geometry_distance >= 0.60:
        return 0.0

    geometry_similarity = max(
        0.0,
        1.0
        - geometry_distance / 0.60,
    )

    score = (
        0.78
        * geometry_similarity
        + 0.22
        * length_similarity
    )

    return round(
        score * 100,
        1,
    )


def _similar_workouts(
    workout,
    history,
    *,
    minimum_score: float = 70.0,
    limit: int = 5,
) -> list[tuple[float, object]]:
    """
    Finds earlier activities with sufficiently similar
    GPS geometry.
    """

    if history is None:
        return []

    current_date = (
        _workout_datetime(
            workout
        )
    )

    current_sport = str(
        workout.sport
        or ""
    ).strip().casefold()

    matches = []

    for candidate in (
        history.workouts
    ):

        if (
            str(
                candidate.workout_id
            )
            == str(
                workout.workout_id
            )
        ):
            continue

        candidate_date = (
            _workout_datetime(
                candidate
            )
        )

        if (
            current_date is not None
            and candidate_date
            is not None
            and candidate_date
            >= current_date
        ):
            continue

        candidate_sport = str(
            candidate.sport
            or ""
        ).strip().casefold()

        if (
            candidate_sport
            != current_sport
        ):
            continue

        if not candidate.sensors.get(
            "gps"
        ):
            continue

        score = (
            _route_similarity_score(
                workout,
                candidate,
            )
        )

        if score < minimum_score:
            continue

        matches.append(
            (
                score,
                candidate,
            )
        )

    matches.sort(
        key=lambda item: (
            item[0],
            (
                _workout_datetime(
                    item[1]
                )
                or datetime.min
            ),
        ),
        reverse=True,
    )

    return matches[
        :limit
    ]


def _route_progress_for_time(
    route,
    timestamp: datetime,
) -> float | None:

    if not route:
        return None

    timestamps = [
        row["Timestamp"]
        for row in route
    ]

    index = bisect_left(
        timestamps,
        timestamp,
    )

    if index <= 0:
        return route[0][
            "Progress"
        ]

    if index >= len(route):
        return route[-1][
            "Progress"
        ]

    before = route[
        index - 1
    ]
    after = route[
        index
    ]

    if (
        timestamp
        - before["Timestamp"]
        <= after["Timestamp"]
        - timestamp
    ):
        return before[
            "Progress"
        ]

    return after[
        "Progress"
    ]

def _route_distance_for_time(
    route,
    timestamp: datetime,
) -> float | None:
    """
    Returns cumulative route distance in kilometres
    for the GPS point nearest to a timestamp.
    """

    if not route:
        return None

    timestamps = [
        row["Timestamp"]
        for row in route
    ]

    index = bisect_left(
        timestamps,
        timestamp,
    )

    if index <= 0:
        return route[0]["Distance"]

    if index >= len(route):
        return route[-1]["Distance"]

    before = route[index - 1]
    after = route[index]

    if (
        timestamp
        - before["Timestamp"]
        <= after["Timestamp"]
        - timestamp
    ):
        return before["Distance"]

    return after["Distance"]

def _sensor_progress_rows(
    workout,
    sensor_name: str,
) -> list[dict]:

    route = (
        _route_profile_rows(
            workout
        )
    )

    if not route:
        return []

    samples = (
        workout.sensors.get(
            sensor_name
        )
        or []
    )

    rows = []

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

        distance = (
            _route_distance_for_time(
                route,
                timestamp,
            )
        )

        if distance is None:
            continue

        rows.append(
            {
                "Distance": distance,
                "Value": numeric_value,
            }
        )

    return rows


def _available_metrics(
    workout,
) -> tuple[str, ...]:

    values = []

    if workout.sensors.get(
        "heart_rate"
    ):
        values.append(
            "Heart rate"
        )

    if workout.sensors.get(
        "power"
    ):
        values.append(
            "Power"
        )

    profile = (
        _route_profile_rows(
            workout
        )
    )

    if any(
        row["Pace"] is not None
        for row in profile
    ):
        values.append(
            "Pace"
        )

    if workout.sensors.get(
        "cadence"
    ):
        values.append(
            "Cadence"
        )

    return tuple(
        values
    )


def _metric_rows(
    workout,
    metric: str,
) -> list[dict]:

    if metric == "Pace":

        return [
            {
                "Distance": (
                    row["Distance"]
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

    sensor_name = {
        "Heart rate": "heart_rate",
        "Power": "power",
        "Cadence": "cadence",
    }[metric]

    return (
        _sensor_progress_rows(
            workout,
            sensor_name,
        )
    )


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
        "Pace": (
            "Pace",
            "min/km",
        ),
        "Cadence": (
            "Cadence",
            "spm",
        ),
    }[metric]


def _workout_label(
    workout,
) -> str:

    title = (
        workout.info.title
        or workout.sport
        or "Activity"
    )

    value = getattr(
        workout,
        "date",
        None,
    )

    if isinstance(
        value,
        datetime,
    ):
        day = value.date()

    else:
        day = value

    if day is None:
        return str(title)

    return (
        f"{title} · "
        f"{day.strftime('%d %b %Y')}"
    )

def _distance_domain(
    *row_groups,
) -> tuple[
    float,
    float,
] | None:
    """
    Returns an exact chart distance domain.

    The final axis value corresponds to the final
    recorded route or sensor distance.
    """

    distances = [
        float(
            row["Distance"]
        )
        for rows in row_groups
        for row in rows
        if (
            isinstance(
                row.get("Distance"),
                (int, float),
            )
            and not isinstance(
                row.get("Distance"),
                bool,
            )
            and row["Distance"] >= 0
        )
    ]

    if not distances:
        return None

    return (
        0.0,
        max(
            distances
        ),
    )

def _comparison_chart(
    workout,
    *,
    metric: str,
    comparison=None,
    height: int = 250,
):
    """
    Overlays one metric from the current activity and,
    optionally, a previous matching route.

    Elevation from the current activity remains a
    low-opacity background.
    """

    current_rows = [
        {
            **row,
            "Activity": (
                _workout_label(
                    workout
                )
            ),
        }
        for row in (
            _metric_rows(
                workout,
                metric,
            )
        )
    ]

    if not current_rows:
        return None

    comparison_rows = []

    if comparison is not None:

        comparison_rows = [
            {
                **row,
                "Activity": (
                    _workout_label(
                        comparison
                    )
                ),
            }
            for row in (
                _metric_rows(
                    comparison,
                    metric,
                )
            )
        ]

    metric_rows = (
        current_rows
        + comparison_rows
    )

    elevation_rows = [
        row
        for row in (
            _route_profile_rows(
                workout
            )
        )
        if row["Elevation"]
        is not None
    ]

    distance_domain = (
        _distance_domain(
            elevation_rows,
            current_rows,
        )
    )

    distance_scale = (
        alt.Scale(
            domain=list(
                distance_domain
            ),
            nice=False,
            zero=True,
        )
        if distance_domain
        is not None
        else alt.Scale(
            nice=False,
            zero=True,
        )
    )

    title, unit = (
        _metric_axis(
            metric
        )
    )

    layers = []

    if elevation_rows:

        elevation_chart = (
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
                    "Distance:Q",
                    title="Distance (km)",
                    scale=distance_scale,
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
                        "Distance:Q",
                        title="Distance (km)",
                        format=".2f",
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
            elevation_chart
        )

    metric_scale = alt.Scale(
        zero=False,
        reverse=(
            metric == "Pace"
        ),
    )

    activity_legend = (
        alt.Legend(
            orient="top",
            direction="horizontal",
            title=None,
        )
        if comparison is not None
        else None
    )

    metric_chart = (
        alt.Chart(
            alt.Data(
                values=metric_rows
            )
        )
        .mark_line(
            strokeWidth=1.9,
        )
        .encode(
            x=alt.X(
                "Distance:Q",
                title="Distance (km)",
                scale=distance_scale,
            ),
            y=alt.Y(
                "Value:Q",
                title=(
                    f"{title} ({unit})"
                ),
                scale=metric_scale,
            ),
            color=alt.Color(
                "Activity:N",
                title=None,
                legend=activity_legend,
            ),
            tooltip=[
                alt.Tooltip(
                    "Activity:N",
                    title="Activity",
                ),
                alt.Tooltip(
                    "Distance:Q",
                    title="Distance (km)",
                    format=".2f",
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
        metric_chart
    )

    return (
        alt.layer(
            *layers
        )
        .resolve_scale(
            y="independent"
        )
        .properties(
            height=height
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
    *,
    history=None,
    key_prefix: str = "activity_analysis",
    show_heading: bool = True,
    compact: bool = False,
    environment_first: bool = True,
) -> None:
    """
    Shows route, performance profile and historical
    comparison for one completed workout.
    """

    if workout is None:
        return

    with st.container(
        border=True
    ):

        if show_heading:
            st.markdown(
                "**Activity analysis**"
            )

        if environment_first:
            (
                temperature_column,
                humidity_column,
                terrain_column,
            ) = st.columns(3, gap="small")

            with temperature_column:
                st.metric(
                    "Air temperature",
                    _environment_label(
                        workout.environment.temperature,
                        suffix=" °C",
                    ),
                )

            with humidity_column:
                st.metric(
                    "Humidity",
                    _environment_label(
                        workout.environment.humidity,
                        suffix="%",
                    ),
                )

            with terrain_column:
                st.metric(
                    "Terrain",
                    workout.environment.terrain or "—",
                )

        metrics = (
            _available_metrics(
                workout
            )
        )

        similar = (
            _similar_workouts(
                workout,
                history,
            )
        )

        # Default chart metric.
        metric = (
            metrics[0]
            if metrics
            else None
        )

        comparison = None

        # ------------------------------------------
        # Route
        # ------------------------------------------

        if workout.sensors.get(
            "gps"
        ):

            st.markdown(
                "**Route**"
            )

            show_route_map(
                workout,
                height=(
                    260
                    if compact
                    else 420
                ),
            )

        # ------------------------------------------
        # Performance graph
        # ------------------------------------------

        if not metrics:

            st.caption(
                "No detailed sensor streams "
                "are available for this activity."
            )
            return

        chart_placeholder = (
            st.empty()
        )

        # ------------------------------------------
        # Comparison controls AFTER graph
        # ------------------------------------------

        st.markdown(
            "**Performance comparison**"
        )

        (
            metric_column,
            compare_column,
        ) = st.columns(
            [1, 1.35],
            gap="small",
        )

        with metric_column:

            metric = st.selectbox(
                "Metric",
                options=metrics,
                key=(
                    f"{key_prefix}_metric"
                ),
            )

        comparison_options = [
            "This activity only"
        ]

        comparison_lookup = {}

        for score, candidate in similar:

            label = (
                f"{_workout_label(candidate)}"
                f" · {score:.0f}% route match"
            )

            comparison_options.append(
                label
            )

            comparison_lookup[
                label
            ] = candidate

        with compare_column:

            comparison_label = (
                st.selectbox(
                    "Compare with",
                    options=(
                        comparison_options
                    ),
                    key=(
                        f"{key_prefix}_comparison"
                    ),
                )
            )

        comparison = (
            comparison_lookup.get(
                comparison_label
            )
        )

        chart = (
            _comparison_chart(
                workout,
                metric=metric,
                comparison=comparison,
                height=(
                    260
                    if compact
                    else 300
                ),
            )
        )

        if chart is not None:

            chart_placeholder.altair_chart(
                chart,
                use_container_width=True,
            )

        if comparison is None:

            if similar:

                st.caption(
                    (
                        f"{len(similar)} similar historical "
                        "route"
                        + (
                            "s"
                            if len(similar) != 1
                            else ""
                        )
                        + " available for comparison."
                    )
                )

            else:

                st.caption(
                    "No sufficiently similar historical "
                    "route was found."
                )

        else:

            selected_score = next(
                (
                    score
                    for score, candidate
                    in similar
                    if candidate
                    is comparison
                ),
                None,
            )

            if selected_score is not None:

                st.caption(
                    "Route similarity · "
                    f"{selected_score:.0f}%"
                )