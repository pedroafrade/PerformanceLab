"""
PerformanceLab

Complete training-plan page.
"""

from datetime import date, timedelta
from html import escape

import altair as alt
import streamlit as st

from performancelab.presentation import (
    PlanPresenter,
)
from .phase_timeline import (
    phase_timeline_from_phases_html,
    phase_timeline_styles,
)
from .summary_cards import (
    summary_cards_html,
    summary_cards_styles,
)
from .workout_table import (
    format_duration,
)


def _status_label(
    status: str,
) -> str:
    """
    Returns a readable planned-workout status.
    """

    return (
        str(status or "pending")
        .replace("_", " ")
        .title()
    )

def _plan_chart_data(
    chart_points,
) -> list[dict]:
    """
    Converts session-level planned load into chart rows.
    """

    rows = []

    for point in chart_points:

        if point.planned_load is None:
            continue

        duration = getattr(
            point,
            "duration",
            None,
        )

        duration_minutes = None

        if duration is not None:

            duration_minutes = round(
                duration.total_seconds()
                / 60
            )
        completed_load = getattr(
            point,
            "completed_load",
            None,
        )

        load_difference = (
            completed_load
            - point.planned_load
            if completed_load is not None
            else None
        )
        rows.append(
            {
                "Date": point.day.isoformat(),
                "Planned load": (
                    point.planned_load
                ),
                "Completed load": (
                    completed_load
                ),
                "Load difference": (
                    load_difference
                ),
                "Distance": getattr(
                    point,
                    "distance",
                    None,
                ),
                "Elevation": getattr(
                    point,
                    "elevation_gain",
                    None,
                ),
                "Duration": (
                    duration_minutes
                ),
                "Session": point.title,
                "Intensity": (
                    getattr(
                        point,
                        "intensity",
                        None,
                    )
                    or "—"
                ),
                "Phase": (
                    point.phase
                    or "Unassigned"
                ),
                "Status": (
                    _status_label(
                        getattr(
                            point,
                            "status",
                            "pending",
                        )
                    )
                ),
                "Session type": (
                    "Race"
                    if point.is_race
                    else "Training"
                ),
            }
        )

    return rows


def _plan_volume_chart_data(
    plan,
) -> list[dict]:
    """
    Builds weekly training volume plus individual races.

    Race distance and elevation are excluded from weekly
    training totals. Race points remain on their exact
    dates, and the final recovery point is placed on the
    exact end date of the plan.
    """

    rows = []

    for week_index, week in enumerate(
        plan.weeks
    ):

        weekly_distance = sum(
            (
                workout.distance
                or 0.0
            )
            for workout in week.workouts
            if not workout.is_race
        )

        weekly_elevation = sum(
            (
                workout.elevation_gain
                or 0.0
            )
            for workout in week.workouts
            if not workout.is_race
        )

        is_final_week = (
            week_index
            == len(plan.weeks) - 1
        )

        weekly_point_date = (
            plan.end_date
            if (
                is_final_week
                and plan.end_date
                is not None
            )
            else week.start_date
        )

        rows.append(
            {
                "Date": (
                    weekly_point_date
                    .isoformat()
                ),
                "Distance": (
                    weekly_distance
                ),
                "Elevation": (
                    weekly_elevation
                ),
                "Point type": (
                    "Weekly training"
                ),
                "Label": (
                    f"{week.start_date.strftime('%d %b')}"
                    " – "
                    f"{week.end_date.strftime('%d %b')}"
                ),
            }
        )

        for workout in week.workouts:

            if not workout.is_race:
                continue

            rows.append(
                {
                    "Date": (
                        workout.scheduled_at
                        .date()
                        .isoformat()
                    ),
                    "Distance": (
                        workout.distance
                        or 0.0
                    ),
                    "Elevation": (
                        workout.elevation_gain
                        or 0.0
                    ),
                    "Point type": "Race",
                    "Label": (
                        getattr(
                            workout,
                            "title",
                            None,
                        )
                        or "Race"
                    ),
                }
            )

    return sorted(
        rows,
        key=lambda row: (
            row["Date"],
            (
                0
                if row["Point type"]
                == "Weekly training"
                else 1
            ),
        ),
    )

def _plan_chart_date_scale(
    plan,
):
    """
    Returns the shared complete-plan date scale.

    The scale includes completed activities exposed by the
    presenter immediately before a midweek plan start.
    """

    if (
        plan.start_date is None
        or plan.end_date is None
    ):
        return alt.Scale()

    completed_days = tuple(
        point.day
        for point in getattr(
            plan,
            "completed_load_points",
            (),
        )
        if point.day is not None
    )

    chart_start_date = (
        min(
            plan.start_date,
            min(completed_days),
        )
        if completed_days
        else plan.start_date
    )

    return alt.Scale(
        domain=[
            chart_start_date.isoformat(),
            plan.end_date.isoformat(),
        ]
    )

def _plan_today_marker_data(
    plan,
    *,
    reference_day: date,
) -> list[dict]:
    """
    Builds the current-day marker when the reference
    day falls inside the plan horizon.
    """

    if (
        plan.start_date is None
        or plan.end_date is None
        or reference_day < plan.start_date
        or reference_day > plan.end_date
    ):
        return []

    return [
        {
            "Date": reference_day.isoformat(),
            "Label": "Today",
        }
    ]


def _plan_today_marker(
    plan,
):
    """
    Builds the vertical current-day chart marker.
    """

    marker_data = (
        _plan_today_marker_data(
            plan,
            reference_day=date.today(),
        )
    )

    return (
        alt.Chart(
            alt.Data(
                values=marker_data
            )
        )
        .mark_rule(
            strokeDash=[4, 4],
            strokeWidth=1.2,
            opacity=0.65,
            color="#6b7280",
        )
        .encode(
            x=alt.X(
                "Date:T",
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Today",
                    format="%d %b %Y",
                ),
            ],
        )
    )

def _completed_load_chart_data(
    completed_load_points,
) -> list[dict]:
    """
    Converts every completed historical activity into a
    chart row, independently of plan reconciliation.
    """

    return [
        {
            "Date": point.day.isoformat(),
            "Session": point.title,
            "Completed load": float(
                point.completed_load
            ),
        }
        for point in completed_load_points
    ]

def _planned_load_chart_series(
    chart_points,
) -> tuple[
    list[dict],
    list[dict],
]:
    """
    Separates training load from race markers.

    Race load remains available in the tooltip, but its
    marker is positioned just above the highest training
    load so that a large race value does not flatten the
    training progression.
    """

    chart_data = (
        _plan_chart_data(
            chart_points
        )
    )

    training_rows = [
        row
        for row in chart_data
        if (
            row["Session type"]
            == "Training"
        )
    ]

    race_rows = [
        row
        for row in chart_data
        if (
            row["Session type"]
            == "Race"
        )
    ]

    training_loads = [
        float(
            row["Planned load"]
        )
        for row in training_rows
    ]

    if training_loads:

        race_marker_load = (
            max(training_loads)
            * 1.08
        )

    else:

        available_loads = [
            float(
                row["Planned load"]
            )
            for row in chart_data
        ]

        race_marker_load = max(
            available_loads,
            default=1.0,
        )

    positioned_races = [
        {
            **row,
            "Marker load": (
                race_marker_load
            ),
        }
        for row in race_rows
    ]

    return (
        training_rows,
        positioned_races,
    )


def _weekly_planned_load_curve_data(
    chart_points,
) -> list[dict]:
    """
    Builds a weekly planned-load curve with isolated
    race peaks.

    The normal weekly value contains training load only.
    Each race produces a peak on its exact date, with
    anchors on the previous and following days.
    """

    valid_points = [
        point
        for point in chart_points
        if point.planned_load is not None
    ]

    if not valid_points:
        return []

    first_curve_day = min(
        point.day
        for point in valid_points
    )

    weeks = {}

    for point in valid_points:

        if point.planned_load is None:
            continue

        week_start = (
            point.day
            - timedelta(
                days=point.day.weekday()
            )
        )

        week_data = weeks.setdefault(
            week_start,
            {
                "training_load": 0.0,
                "races": [],
            },
        )

        if point.is_race:

            week_data["races"].append(
                {
                    "day": point.day,
                    "load": float(
                        point.planned_load
                    ),
                    "title": (
                        point.title
                        or "Race"
                    ),
                }
            )

        else:

            week_data["training_load"] += float(
                point.planned_load
            )

    weekly_training_loads = {
        week_start: week_data["training_load"]
        for week_start, week_data
        in weeks.items()
    }

    rows_by_date = {}

    def add_row(
        *,
        day,
        load,
        point_type,
        label,
        priority,
    ) -> None:

        existing = rows_by_date.get(
            day
        )

        if (
            existing is not None
            and existing["_priority"]
            > priority
        ):
            return

        rows_by_date[day] = {
            "Date": day.isoformat(),
            "Weekly load": float(
                load
            ),
            "Point type": point_type,
            "Label": label,
            "_priority": priority,
        }

    for week_start, week_data in sorted(
        weeks.items()
    ):

        training_load = (
            week_data["training_load"]
        )

        weekly_point_day = max(
            week_start,
            first_curve_day,
        )

        add_row(
            day=weekly_point_day,
            load=training_load,
            point_type="Weekly training",
            label="Weekly training load",
            priority=1,
        )

        for race in sorted(
            week_data["races"],
            key=lambda item: item["day"],
        ):

            race_day = race["day"]

            day_before = (
                race_day
                - timedelta(
                    days=1
                )
            )

            day_after = (
                race_day
                + timedelta(
                    days=1
                )
            )

            if day_before >= week_start:

                add_row(
                    day=day_before,
                    load=training_load,
                    point_type="Pre-race anchor",
                    label="Weekly training load",
                    priority=2,
                )

            add_row(
                day=race_day,
                load=(
                    training_load
                    + race["load"]
                ),
                point_type="Race peak",
                label=race["title"],
                priority=3,
            )

            following_week_start = (
                day_after
                - timedelta(
                    days=day_after.weekday()
                )
            )

            if following_week_start == week_start:

                following_load = (
                    training_load
                )

            else:

                following_load = (
                    weekly_training_loads.get(
                        following_week_start,
                        0.0,
                    )
                )

            add_row(
                day=day_after,
                load=following_load,
                point_type="Post-race anchor",
                label="Following weekly training load",
                priority=2,
            )

    return [
        {
            key: value
            for key, value in row.items()
            if key != "_priority"
        }
        for _, row in sorted(
            rows_by_date.items()
        )
    ]

def _planned_load_chart(
    plan,
):
    """
    Builds session load and weekly total load using
    independent vertical scales.

    Session load uses the left axis. Weekly total load
    uses the right axis and includes isolated race peaks.
    """

    (
        training_data,
        race_data,
    ) = _planned_load_chart_series(
        plan.chart_points
    )

    weekly_load_data = (
        _weekly_planned_load_curve_data(
            plan.chart_points
        )
    )

    training_base = (
        alt.Chart(
            alt.Data(
                values=training_data
            )
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Session:N",
                    title="Session",
                ),
                alt.Tooltip(
                    "Duration:Q",
                    title="Duration (min)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Intensity:N",
                    title="Intensity",
                ),
                alt.Tooltip(
                    "Planned load:Q",
                    title="Load (AU)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Distance:Q",
                    title="Distance (km)",
                    format=".1f",
                ),
                alt.Tooltip(
                    "Elevation:Q",
                    title="Elevation (m+)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phase:N",
                    title="Phase",
                ),
                alt.Tooltip(
                    "Status:N",
                    title="Status",
                ),
            ],
        )
    )

    training_line = (
        training_base
        .mark_line(
            interpolate="monotone",
            strokeWidth=1.6,
            opacity=0.72,
        )
        .encode(
            y=alt.Y(
                "Planned load:Q",
                title="Session load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
        )
    )

    training_points = (
        training_base
        .mark_point(
            filled=True,
            size=42,
            opacity=0.85,
        )
        .encode(
            y=alt.Y(
                "Planned load:Q",
                title="Session load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
        )
    )

    completed_rows = (
        _completed_load_chart_data(
            plan.completed_load_points
        )
    )

    completed_base = (
        alt.Chart(
            alt.Data(
                values=completed_rows
            )
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Session:N",
                    title="Activity",
                ),
                alt.Tooltip(
                    "Completed load:Q",
                    title="Completed",
                    format=".0f",
                ),
            ],
        )
    )

    completed_line = (
        completed_base
        .mark_line(
            interpolate="linear",
            strokeWidth=2.4,
            color="#16a34a",
        )
        .encode(
            y=alt.Y(
                "Completed load:Q",
                title="Session load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
        )
    )

    completed_points = (
        completed_base
        .mark_point(
            filled=True,
            size=64,
            color="#16a34a",
            stroke="white",
            strokeWidth=0.6,
        )
        .encode(
            y=alt.Y(
                "Completed load:Q",
                title="Session load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
        )
    )

    race_base = (
        alt.Chart(
            alt.Data(
                values=race_data
            )
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Race date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Session:N",
                    title="Race",
                ),
                alt.Tooltip(
                    "Duration:Q",
                    title="Duration (min)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Planned load:Q",
                    title="Race load (AU)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Distance:Q",
                    title="Distance (km)",
                    format=".1f",
                ),
                alt.Tooltip(
                    "Elevation:Q",
                    title="Elevation (m+)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Phase:N",
                    title="Phase",
                ),
            ],
        )
    )

    race_rules = (
        race_base
        .mark_rule(
            strokeDash=[
                3,
                4,
            ],
            strokeWidth=0.8,
            opacity=0.22,
            color="#ff4b4b",
        )
    )

    race_points = (
        race_base
        .mark_point(
            filled=True,
            shape="diamond",
            size=90,
            color="#ff4b4b",
        )
        .encode(
            y=alt.Y(
                "Marker load:Q",
                title="Session load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
        )
    )

    weekly_load_line = (
        alt.Chart(
            alt.Data(
                values=weekly_load_data
            )
        )
        .mark_line(
            interpolate="linear",
            strokeDash=[
                5,
                4,
            ],
            strokeWidth=1.2,
            opacity=0.3,
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
            y=alt.Y(
                "Weekly load:Q",
                title="Weekly total load (AU)",
                axis=alt.Axis(
                    orient="right",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Weekly load:Q",
                    title="Weekly total",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Point type:N",
                    title="Point",
                ),
                alt.Tooltip(
                    "Label:N",
                    title="Description",
                ),
            ],
        )
    )

    session_load_chart = (
        alt.layer(
            training_line,
            training_points,
            completed_line,
            completed_points,
            race_rules,
            race_points,
        )
    )

    today_marker = (
        _plan_today_marker(
            plan
        )
    )

    return (
        alt.layer(
            session_load_chart,
            weekly_load_line,
            today_marker,
        )
        .resolve_scale(
            y="independent"
        )
        .properties(
            height=115,
        )
        .configure_axis(
            grid=True,
            gridOpacity=0.08,
            gridWidth=0.5,
            domainOpacity=0.28,
            tickOpacity=0.28,
            labelFontSize=9,
            titleFontSize=10,
            labelPadding=3,
            titlePadding=6,
        )
    )
def _plan_load_legend_html() -> str:
    """
    Builds a compact legend for the plan load chart.
    """

    return """
    <div class="plan-load-legend">
        <span class="plan-load-legend-item">
            <span class="plan-load-line planned"></span>
            Planned
        </span>
        <span class="plan-load-legend-item">
            <span class="plan-load-line completed"></span>
            Completed
        </span>
        <span class="plan-load-legend-item">
            <span class="plan-load-line weekly"></span>
            Weekly total
        </span>
        <span class="plan-load-legend-item">
            <span class="plan-load-race"></span>
            Race
        </span>
    </div>
    """

def _distance_elevation_chart(
    plan,
):
    """
    Builds the weekly distance and elevation chart.

    Distance uses a continuous line with weekly training
    circles and race diamonds. Elevation uses only a
    dashed line to reduce visual noise.
    """

    chart_data = (
        _plan_volume_chart_data(
            plan
        )
    )

    base = (
        alt.Chart(
            alt.Data(
                values=chart_data
            )
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                scale=_plan_chart_date_scale(
                    plan
                ),
            ),
        )
    )

    shared_tooltip = [
        alt.Tooltip(
            "Date:T",
            title="Date",
            format="%d %b %Y",
        ),
        alt.Tooltip(
            "Point type:N",
            title="Type",
        ),
        alt.Tooltip(
            "Label:N",
            title="Session / week",
        ),
        alt.Tooltip(
            "Distance:Q",
            title="Distance (km)",
            format=".1f",
        ),
        alt.Tooltip(
            "Elevation:Q",
            title="Elevation (m+)",
            format=".0f",
        ),
    ]

    distance_line = (
        base
        .mark_line(
            interpolate="monotone",
            strokeWidth=1.8,
        )
        .encode(
            y=alt.Y(
                "Distance:Q",
                title="Distance (km)",
                scale=alt.Scale(
                    zero=True
                ),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Distance",
                        "Elevation",
                    ],
                ),
                legend=alt.Legend(
                    orient="top",
                    direction="horizontal",
                    columns=2,
                    title=None,
                    labelFontSize=9,
                    symbolSize=45,
                    offset=2,
                    padding=0,
                ),
            ),
            tooltip=shared_tooltip,
        )
        .transform_calculate(
            Metric="'Distance'"
        )
    )

    weekly_distance_points = (
        base
        .transform_filter(
            (
                "datum['Point type'] "
                "=== 'Weekly training'"
            )
        )
        .mark_point(
            filled=True,
            size=36,
            opacity=0.78,
        )
        .encode(
            y=alt.Y(
                "Distance:Q",
                axis=None,
                scale=alt.Scale(
                    zero=True
                ),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Distance",
                        "Elevation",
                    ],
                ),
                legend=None,
            ),
            tooltip=shared_tooltip,
        )
        .transform_calculate(
            Metric="'Distance'"
        )
    )

    race_distance_points = (
        base
        .transform_filter(
            (
                "datum['Point type'] "
                "=== 'Race'"
            )
        )
        .mark_point(
            filled=True,
            shape="diamond",
            size=88,
        )
        .encode(
            y=alt.Y(
                "Distance:Q",
                axis=None,
                scale=alt.Scale(
                    zero=True
                ),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Distance",
                        "Elevation",
                    ],
                ),
                legend=None,
            ),
            tooltip=shared_tooltip,
        )
        .transform_calculate(
            Metric="'Distance'"
        )
    )

    elevation_line = (
        base
        .mark_line(
            interpolate="monotone",
            strokeDash=[
                5,
                4,
            ],
            strokeWidth=1.5,
            opacity=0.82,
        )
        .encode(
            y=alt.Y(
                "Elevation:Q",
                title="Elevation (m D+)",
                axis=alt.Axis(
                    orient="right",
                ),
                scale=alt.Scale(
                    zero=True
                ),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Distance",
                        "Elevation",
                    ],
                ),
                legend=None,
            ),
            tooltip=shared_tooltip,
        )
        .transform_calculate(
            Metric="'Elevation'"
        )
    )

    today_marker = (
        _plan_today_marker(
            plan
        )
    )

    return (
        alt.layer(
            distance_line,
            weekly_distance_points,
            race_distance_points,
            elevation_line,
            today_marker,
        )
        .resolve_scale(
            y="independent"
        )
        .properties(
            height=125,
        )
        .configure_axis(
            grid=True,
            gridOpacity=0.08,
            gridWidth=0.5,
            domainOpacity=0.28,
            tickOpacity=0.28,
            labelFontSize=9,
            titleFontSize=10,
            labelPadding=3,
            titlePadding=6,
        )
    )

def _plan_summary_metrics(
    plan,
) -> dict[str, str]:
    """
    Builds concise summary values for the complete plan.
    """

    total_load = sum(
        week.planned_load
        for week in plan.weeks
    )

    max_distance = max(
        (
            point.distance
            for point in plan.progression
        ),
        default=0.0,
    )

    max_elevation = max(
        (
            point.elevation_gain
            for point in plan.progression
        ),
        default=0.0,
    )

    return {
        "Horizon": (
            f"{len(plan.weeks)} weeks"
        ),
        "Planned load": (
            f"{total_load:.0f} AU"
        ),
        "Max distance": (
            f"{max_distance:.0f} km/week"
        ),
        "Max elevation": (
            f"{max_elevation:.0f} m/week"
        ),
    }

def _current_plan_week(
    weeks,
    *,
    reference_day: date,
):
    """
    Returns the plan week containing the reference day.
    """

    return next(
        (
            week
            for week in weeks
            if (
                week.start_date
                <= reference_day
                <= week.end_date
            )
        ),
        None,
    )

def _week_duration_label(
    week,
) -> str:
    """
    Formats the total duration of a plan week.
    """

    total_seconds = sum(
        (
            workout.duration
            .total_seconds()
        )
        for workout in week.workouts
        if workout.duration is not None
    )

    total_minutes = round(
        total_seconds / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return f"{hours}h{minutes:02d}"

    if hours:
        return f"{hours}h"

    return f"{minutes} min"



def _week_is_current(
    week,
    *,
    reference_day: date,
) -> bool:
    """
    Returns whether the reference day belongs to the week.
    """

    return (
        week.start_date
        <= reference_day
        <= week.end_date
    )

def _week_summary_label(
    week,
    *,
    reference_day: date,
) -> str:
    """
    Builds the compact summary shown in the week list.
    """

    phase = (
        str(
            week.phase
            or "Unassigned"
        )
        .strip()
    )

    session_count = len(
        week.workouts
    )

    session_label = (
        "session"
        if session_count == 1
        else "sessions"
    )

    duration = (
        _week_duration_label(
            week
        )
    )

    current_marker = (
        "● "
        if _week_is_current(
            week,
            reference_day=reference_day,
        )
        else ""
    )

    return (
        f"{current_marker}"
        f"{week.start_date.strftime('%d %b')}"
        " – "
        f"{week.end_date.strftime('%d %b')}"
        "  ·  "
        f"{phase}"
        "  ·  "
        f"{session_count} {session_label}"
        "  ·  "
        f"{duration}"
        "  ·  "
        f"{week.planned_load:.0f} AU"
    )

def _week_focus_items(
    week,
) -> tuple[str, ...]:
    """
    Builds a concise training focus from the sessions
    already present in one plan week.
    """

    focus_items = []

    def add_focus(
        label: str,
    ) -> None:

        if (
            label not in focus_items
            and len(focus_items) < 3
        ):
            focus_items.append(
                label
            )

    for workout in week.workouts:

        title = (
            str(
                workout.title
                or ""
            )
            .strip()
            .lower()
        )

        intensity = (
            str(
                workout.intensity
                or ""
            )
            .strip()
            .lower()
        )

        if workout.is_race:

            add_focus(
                "Execute the target event"
            )

            continue

        if (
            "lt2" in title
            or "threshold" in title
        ):

            add_focus(
                "Develop LT2 durability"
            )

        elif (
            "vo2" in title
            or "vo₂" in title
        ):

            add_focus(
                "Maintain VO₂max stimulus"
            )

        elif (
            "long run" in title
            or "long trail" in title
        ):

            add_focus(
                "Build aerobic durability"
            )

        elif (
            "hill" in title
            or "climb" in title
        ):

            add_focus(
                "Develop climbing strength"
            )

        elif (
            "shakeout" in title
            or "pre-race" in title
            or "pre race" in title
        ):

            add_focus(
                "Preserve race readiness"
            )

        elif (
            "recovery" in title
            or intensity == "recovery"
        ):

            add_focus(
                "Promote recovery"
            )

    phase = (
        str(
            getattr(
                week,
                "phase",
                "",
            )
            or ""
        )
        .strip()
        .lower()
    )

    phase_focus = {
        "build": (
            "Build sustainable aerobic capacity"
        ),
        "peak": (
            "Prioritise race-specific quality"
        ),
        "taper": (
            "Reduce fatigue and preserve readiness"
        ),
        "race": (
            "Preserve freshness for competition"
        ),
        "transition": (
            "Restore freshness"
        ),
        "regeneration": (
            "Restore freshness"
        ),
    }

    fallback = phase_focus.get(
        phase
    )

    if fallback is not None:

        add_focus(
            fallback
        )

    return tuple(
        focus_items
    )

def _week_html(
    week,
) -> str:
    """
    Renders the workouts of one plan week.
    """

    parts = [
        '<div class="complete-plan-week">'
    ]

    focus_items = (
        _week_focus_items(
            week
        )
    )

    if focus_items:

        focus_html = "".join(
            (
                '<span class="complete-plan-focus-item">'
                f"{escape(item)}"
                "</span>"
            )
            for item in focus_items
        )

        parts.append(
            (
                '<section class="complete-plan-focus">'
                '<div class="complete-plan-focus-label">'
                "Week focus"
                "</div>"
                '<div class="complete-plan-focus-items">'
                f"{focus_html}"
                "</div>"
                "</section>"
            )
        )

    race_workouts = tuple(
        workout
        for workout in week.workouts
        if workout.is_race
    )

    for race in race_workouts:

        race_title = escape(
            str(
                race.title
                or "Target event"
            )
        )

        race_date = (
            race.scheduled_at
            .strftime("%d %b")
        )

        race_details = [
            race_date
        ]

        distance = getattr(
            race,
            "distance",
            None,
        )

        if distance is not None:

            race_details.append(
                f"{distance:g} km"
            )

        elevation_gain = getattr(
            race,
            "elevation_gain",
            None,
        )

        if elevation_gain is not None:

            race_details.append(
                f"+{elevation_gain:g} m"
            )

        parts.append(
            (
                '<section class="complete-plan-event">'
                '<div class="complete-plan-event-label">'
                '<span class="complete-plan-event-icon">'
                "◆"
                "</span>"
                "<span>Target event</span>"
                "</div>"
                '<div class="complete-plan-event-title">'
                f"{race_title}"
                "</div>"
                '<div class="complete-plan-event-details">'
                f"{escape(' · '.join(race_details))}"
                "</div>"
                "</section>"
            )
        )

    for workout in week.workouts:

        normalized_status = (
            str(
                workout.status
                or "pending"
            )
            .strip()
            .lower()
            .replace(
                "_",
                "-",
            )
        )

        status_label = escape(
            _status_label(
                workout.status
            )
        )

        title = escape(
            str(
                workout.title
                or "Planned workout"
            )
        )

        sport = escape(
            str(
                workout.sport
                or "Rest"
            )
        )

        intensity = escape(
            str(
                workout.intensity
                or "—"
            )
        )

        duration = escape(
            format_duration(
                workout.duration
            )
        )

        planned_load = (
            (
                f"{workout.planned_load:.0f} AU"
            )
            if workout.planned_load is not None
            else "—"
        )

        prescription = (
            escape(
                str(
                    workout.prescription_summary
                )
            )
            if workout.prescription_summary
            else ""
        )

        marker_class = (
            _sidebar_session_marker_class(
                workout
            )
        )

        day_name = (
            workout.scheduled_at
            .strftime("%a")
            .upper()
        )

        day_number = (
            workout.scheduled_at
            .strftime("%d")
        )

        parts.append(
            (
                '<article class="complete-plan-session '
                f'status-{escape(normalized_status)}">'
                '<div class="complete-plan-session-date">'
                '<span class="complete-plan-session-day">'
                f"{escape(day_name)}"
                "</span>"
                '<span class="complete-plan-session-day-number">'
                f"{escape(day_number)}"
                "</span>"
                "</div>"
                '<span class="complete-plan-session-marker '
                f'{escape(marker_class)}"></span>'
                '<div class="complete-plan-session-main">'
                '<div class="complete-plan-session-title">'
                f"{title}"
                "</div>"
                '<div class="complete-plan-session-context">'
                f"<span>{sport}</span>"
            )
        )

        if prescription:

            parts.append(
                (
                    '<span class="complete-plan-session-separator">'
                    "·"
                    "</span>"
                    '<span class="complete-plan-prescription">'
                    f"{prescription}"
                    "</span>"
                )
            )

        parts.append(
            (
                "</div>"
                "</div>"
                '<div class="complete-plan-session-metric">'
                '<span class="complete-plan-session-metric-label">'
                "Duration"
                "</span>"
                '<span class="complete-plan-session-metric-value">'
                f"{duration}"
                "</span>"
                "</div>"
                '<div class="complete-plan-session-metric">'
                '<span class="complete-plan-session-metric-label">'
                "Load"
                "</span>"
                '<span class="complete-plan-session-metric-value">'
                f"{escape(planned_load)}"
                "</span>"
                "</div>"
                '<div class="complete-plan-session-metric">'
                '<span class="complete-plan-session-metric-label">'
                "Intensity"
                "</span>"
                '<span class="complete-plan-session-metric-value">'
                f"{intensity}"
                "</span>"
                "</div>"
                '<div class="complete-plan-session-status '
                f'status-{escape(normalized_status)}">'
                f"{status_label}"
                "</div>"
                "</article>"
            )
        )

    parts.append(
        (
            '<div class="complete-plan-week-spacer" '
            'aria-hidden="true"></div>'
            "</div>"
        )
    )

    return "".join(
        parts
    )

def _sidebar_phase_html(
    current_phase,
) -> str:
    """
    Builds the current-phase sidebar card.
    """

    if current_phase is None:
        return (
            '<section class="plan-sidebar-card">'
            '<div class="plan-sidebar-heading">'
            '<span class="plan-sidebar-icon">◎</span>'
            "<span>Current phase</span>"
            "</div>"
            '<p class="plan-sidebar-empty">'
            "No current phase."
            "</p>"
            "</section>"
        )

    phase_name = escape(
        str(
            current_phase.name
            or "Unassigned"
        )
    )

    objective = escape(
        str(
            current_phase.objective
            or ""
        )
    )

    date_range = (
        f"{current_phase.start_date.strftime('%d %b')} "
        "– "
        f"{current_phase.end_date.strftime('%d %b')}"
    )

    weeks_remaining = max(
        0,
        int(
            current_phase.weeks_remaining
        ),
    )

    sessions_remaining = max(
        0,
        int(
            current_phase.sessions_remaining
        ),
    )

    planned_load_remaining = max(
        0.0,
        float(
            current_phase
            .planned_load_remaining
        ),
    )

    longest_session_minutes = max(
        0,
        int(
            current_phase
            .longest_session_minutes
        ),
    )

    weeks_label = (
        "week"
        if weeks_remaining == 1
        else "weeks"
    )

    sessions_label = (
        "session"
        if sessions_remaining == 1
        else "sessions"
    )

    return (
        '<section class="plan-sidebar-card '
        'plan-sidebar-phase-card">'
        '<div class="plan-sidebar-heading">'
        '<span class="plan-sidebar-icon">◎</span>'
        "<span>Current phase</span>"
        "</div>"
        '<div class="plan-sidebar-phase-name">'
        f"{phase_name}"
        "</div>"
        '<div class="plan-sidebar-date-range">'
        f"{escape(date_range)}"
        "</div>"
        '<p class="plan-sidebar-objective">'
        f"{objective}"
        "</p>"
        '<div class="plan-sidebar-divider"></div>'
        '<div class="plan-sidebar-phase-metrics">'
        '<div class="plan-sidebar-phase-metric">'
        '<span class="plan-sidebar-phase-metric-value">'
        f"{weeks_remaining}"
        "</span>"
        '<span class="plan-sidebar-phase-metric-label">'
        f"{weeks_label} left"
        "</span>"
        "</div>"
        '<div class="plan-sidebar-phase-metric">'
        '<span class="plan-sidebar-phase-metric-value">'
        f"{sessions_remaining}"
        "</span>"
        '<span class="plan-sidebar-phase-metric-label">'
        f"{sessions_label} left"
        "</span>"
        "</div>"
        '<div class="plan-sidebar-phase-metric">'
        '<span class="plan-sidebar-phase-metric-value">'
        f"{planned_load_remaining:.0f}"
        "</span>"
        '<span class="plan-sidebar-phase-metric-label">'
        "AU remaining"
        "</span>"
        "</div>"
        '<div class="plan-sidebar-phase-metric">'
        '<span class="plan-sidebar-phase-metric-value">'
        f"{longest_session_minutes}"
        "</span>"
        '<span class="plan-sidebar-phase-metric-label">'
        "max minutes"
        "</span>"
        "</div>"
        "</div>"
        "</section>"
    )


def _sidebar_session_marker_class(
    workout,
) -> str:
    """
    Returns the visual marker class for one workout.
    """

    if workout.is_race:
        return "race"

    intensity = (
        str(
            workout.intensity
            or ""
        )
        .strip()
        .lower()
    )

    title = (
        str(
            workout.title
            or ""
        )
        .strip()
        .lower()
    )

    if (
        intensity
        in {
            "hard",
            "very hard",
            "moderately hard",
        }
        or "lt2" in title
        or "tempo" in title
        or "vo₂" in title
        or "vo2" in title
        or "hill" in title
        or "speed" in title
    ):
        return "quality"

    return "aerobic"


def _sidebar_week_html(
    week,
) -> str:
    """
    Builds the current-week sidebar card.
    """

    if week is None:
        return (
            '<section class="plan-sidebar-card">'
            '<div class="plan-sidebar-heading">'
            '<span class="plan-sidebar-icon">▣</span>'
            "<span>Current week</span>"
            "</div>"
            '<p class="plan-sidebar-empty">'
            "No current plan week."
            "</p>"
            "</section>"
        )

    phase = escape(
        str(
            week.phase
            or "Unassigned"
        )
    )

    date_range = (
        f"{week.start_date.strftime('%d %b')} "
        "– "
        f"{week.end_date.strftime('%d %b')}"
    )

    session_count = len(
        week.workouts
    )

    duration = escape(
        _week_duration_label(
            week
        )
    )

    planned_load = (
        f"{week.planned_load:.0f} AU"
    )

    session_rows = []

    for workout in week.workouts:

        marker_class = (
            _sidebar_session_marker_class(
                workout
            )
        )

        day_label = (
            workout.scheduled_at
            .strftime("%a %d")
            .upper()
        )

        title = escape(
            str(
                workout.title
                or "Planned workout"
            )
        )

        session_rows.append(
            (
                '<div class="plan-sidebar-session">'
                '<span class="plan-sidebar-session-marker '
                f'{marker_class}"></span>'
                '<span class="plan-sidebar-session-day">'
                f"{escape(day_label)}"
                "</span>"
                '<span class="plan-sidebar-session-title">'
                f"{title}"
                "</span>"
                "</div>"
            )
        )

    sessions_html = "".join(
        session_rows
    )

    session_label = (
        "session"
        if session_count == 1
        else "sessions"
    )

    return (
        '<section class="plan-sidebar-card '
        'plan-sidebar-week-card">'
        '<div class="plan-sidebar-heading">'
        '<span class="plan-sidebar-icon">▣</span>'
        "<span>Current week</span>"
        "</div>"
        '<div class="plan-sidebar-week-range">'
        f"{escape(date_range)}"
        "</div>"
        '<div class="plan-sidebar-week-phase">'
        f"{phase}"
        "</div>"
        '<div class="plan-sidebar-week-summary">'
        "<span>"
        f"{session_count} {session_label}"
        "</span>"
        "<span>·</span>"
        "<span>"
        f"{duration}"
        "</span>"
        "<span>·</span>"
        "<span>"
        f"{escape(planned_load)}"
        "</span>"
        "</div>"
        '<div class="plan-sidebar-sessions">'
        f"{sessions_html}"
        "</div>"
        "</section>"
    )

def _adaptation_metric_rows(
    adaptation,
    *,
    adjusted: bool,
) -> tuple[str, ...]:
    """
    Builds visible before/after metrics for the plan
    adaptation card.
    """

    prefix = (
        "revised"
        if adjusted
        else "previous"
    )

    rows = []

    minutes = getattr(
        adaptation,
        f"{prefix}_minutes",
        None,
    )

    if minutes is not None:
        rows.append(
            f"{minutes} min"
        )

    distance = getattr(
        adaptation,
        f"{prefix}_distance",
        None,
    )

    if distance is not None:
        rows.append(
            f"{distance:g} km"
        )

    elevation = getattr(
        adaptation,
        f"{prefix}_elevation_gain",
        None,
    )

    if elevation is not None:
        rows.append(
            f"+{elevation:g} m D+"
        )

    prescription = getattr(
        adaptation,
        f"{prefix}_prescription",
        None,
    )

    if prescription:
        rows.append(
            str(
                prescription
            )
        )

    return tuple(
        rows
    )


def _sidebar_adaptation_column_html(
    *,
    label: str,
    title: str,
    rows: tuple[str, ...],
    adjusted: bool,
) -> str:
    """
    Builds one before/after adaptation column.
    """

    modifier = (
        " adjusted"
        if adjusted
        else ""
    )

    metrics = "".join(
        (
            '<div class="plan-sidebar-adaptation-metric">'
            f"{escape(row)}"
            "</div>"
        )
        for row in rows
    )

    return (
        '<div class="plan-sidebar-adaptation-column'
        f'{modifier}">'
        '<div class="plan-sidebar-adaptation-column-label">'
        f"{escape(label)}"
        "</div>"
        '<div class="plan-sidebar-adaptation-column-title">'
        f"{escape(title)}"
        "</div>"
        '<div class="plan-sidebar-adaptation-metrics">'
        f"{metrics}"
        "</div>"
        "</div>"
    )

def _sidebar_adaptation_html(
    adaptation,
    *,
    reference_day: date,
) -> str:
    """
    Builds the latest-adaptation sidebar card.
    """

    if adaptation is None:
        return (
            '<section class="plan-sidebar-card">'
            '<div class="plan-sidebar-heading">'
            '<span class="plan-sidebar-icon">↻</span>'
            "<span>Latest adaptation</span>"
            "</div>"
            '<p class="plan-sidebar-empty">'
            "No adaptations applied yet."
            "</p>"
            "</section>"
        )

    days_ago = max(
        0,
        (
            reference_day
            - adaptation.reconciled_on
        ).days,
    )

    if days_ago == 0:
        date_label = "Today"
    elif days_ago == 1:
        date_label = "1 day ago"
    else:
        date_label = f"{days_ago} days ago"

    reason = escape(
        str(
            adaptation.reason
            or ""
        )
    )

    planned_rows = (
        _adaptation_metric_rows(
            adaptation,
            adjusted=False,
        )
    )

    adjusted_rows = (
        _adaptation_metric_rows(
            adaptation,
            adjusted=True,
        )
    )

    planned_html = (
        _sidebar_adaptation_column_html(
            label="Planned session",
            title=(
                adaptation.workout_title
                or "Planned workout"
            ),
            rows=planned_rows,
            adjusted=False,
        )
    )

    adjusted_html = (
        _sidebar_adaptation_column_html(
            label="Adjusted session",
            title=(
                adaptation.workout_title
                or "Planned workout"
            ),
            rows=adjusted_rows,
            adjusted=True,
        )
    )

    return (
        '<section class="plan-sidebar-card '
        'plan-sidebar-adaptation-card">'
        '<div class="plan-sidebar-heading">'
        '<span class="plan-sidebar-icon">↻</span>'
        "<span>Latest adaptation</span>"
        "</div>"
        '<div class="plan-sidebar-adaptation-context">'
        f"<span>{escape(date_label)}</span>"
        "<span>·</span>"
        f"<span>{reason}</span>"
        "</div>"
        '<div class="plan-sidebar-adaptation-comparison">'
        f"{planned_html}"
        '<div class="plan-sidebar-adaptation-arrow">'
        "→"
        "</div>"
        f"{adjusted_html}"
        "</div>"
        '<div class="plan-sidebar-adaptation-status-row">'
        '<span class="plan-sidebar-adaptation-status">'
        "Applied"
        "</span>"
        "</div>"
        "</section>"
    )

def _sidebar_styles() -> str:
    """
    Returns the styles for the plan sidebar cards.
    """

    return """
.plan-sidebar-stack {
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
}

.plan-sidebar-card {
    padding: 0.8rem;
    border: 1px solid rgba(128, 128, 128, 0.25);
    border-radius: 0.7rem;
    background: rgba(128, 128, 128, 0.018);
    box-sizing: border-box;
}

.plan-sidebar-heading {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    margin-bottom: 0.7rem;
    font-size: 0.82rem;
    font-weight: 700;
    line-height: 1.1;
}

.plan-sidebar-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.1rem;
    height: 1.1rem;
    font-size: 1rem;
    line-height: 1;
}

.plan-sidebar-phase-name {
    margin-bottom: 0.4rem;
    color: #ff4b4b;
    font-size: 1.55rem;
    font-weight: 750;
    line-height: 1.05;
}

.plan-sidebar-date-range {
    margin-bottom: 0.6rem;
    font-size: 0.72rem;
    opacity: 0.6;
}

.plan-sidebar-objective {
    margin: 0;
    font-size: 0.8rem;
    line-height: 1.4;
}

.plan-sidebar-divider {
    height: 1px;
    margin: 0.7rem 0 0.6rem 0;
    background: rgba(128, 128, 128, 0.17);
}

.plan-sidebar-phase-metrics {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.45rem;
}

.plan-sidebar-phase-metric {
    display: flex;
    min-width: 0;
    flex-direction: column;
    gap: 0.12rem;
    padding: 0.45rem 0.5rem;
    border: 1px solid rgba(128, 128, 128, 0.16);
    border-radius: 0.5rem;
    background: rgba(128, 128, 128, 0.025);
    box-sizing: border-box;
}

.plan-sidebar-phase-metric-value {
    overflow: hidden;
    font-size: 1rem;
    font-weight: 700;
    line-height: 1;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-sidebar-phase-metric-label {
    overflow: hidden;
    font-size: 0.61rem;
    line-height: 1.15;
    opacity: 0.6;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-sidebar-week-range {
    margin-bottom: 0.35rem;
    font-size: 1.3rem;
    font-weight: 700;
    line-height: 1.1;
}

.plan-sidebar-week-phase {
    margin-bottom: 0.7rem;
    font-size: 0.72rem;
    opacity: 0.6;
}

.plan-sidebar-week-summary {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.3rem;
    margin-bottom: 0.65rem;
    font-size: 0.72rem;
    opacity: 0.72;
}

.plan-sidebar-sessions {
    display: flex;
    flex-direction: column;
    border: 1px solid rgba(128, 128, 128, 0.17);
    border-radius: 0.55rem;
    overflow: hidden;
}

.plan-sidebar-session {
    display: grid;
    grid-template-columns:
        0.55rem
        minmax(3.2rem, 0.8fr)
        minmax(0, 2fr);
    gap: 0.45rem;
    align-items: center;
    min-height: 2.1rem;
    padding: 0.35rem 0.5rem;
    box-sizing: border-box;
}

.plan-sidebar-session + .plan-sidebar-session {
    border-top: 1px solid rgba(128, 128, 128, 0.12);
}

.plan-sidebar-session-marker {
    display: inline-block;
    width: 0.42rem;
    height: 0.42rem;
    border-radius: 50%;
    background: #4f86f7;
}

.plan-sidebar-session-marker.quality {
    background: #ff4b4b;
}

.plan-sidebar-session-marker.race {
    border-radius: 1px;
    background: #ff4b4b;
    transform: rotate(45deg);
}

.plan-sidebar-session-day {
    font-size: 0.66rem;
    font-weight: 700;
    white-space: nowrap;
}

.plan-sidebar-session-title {
    min-width: 0;
    overflow: hidden;
    font-size: 0.74rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-sidebar-adaptation-context {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.3rem;
    margin-bottom: 0.7rem;
    font-size: 0.68rem;
    line-height: 1.35;
    opacity: 0.62;
}

.plan-sidebar-adaptation-comparison {
    display: grid;
    grid-template-columns:
        minmax(0, 1fr)
        1.65rem
        minmax(0, 1fr);
    gap: 0.35rem;
    align-items: stretch;
}

.plan-sidebar-adaptation-column {
    min-width: 0;
    padding: 0.45rem 0.48rem;
    border: 1px solid rgba(128, 128, 128, 0.16);
    border-radius: 0.45rem;
    background: rgba(128, 128, 128, 0.018);
    box-sizing: border-box;
}

.plan-sidebar-adaptation-column.adjusted {
    background: rgba(57, 169, 107, 0.045);
}

.plan-sidebar-adaptation-column-label {
    margin-bottom: 0.25rem;
    font-size: 0.52rem;
    font-weight: 750;
    text-transform: uppercase;
    opacity: 0.52;
}

.plan-sidebar-adaptation-column-title {
    overflow: hidden;
    margin-bottom: 0.28rem;
    font-size: 0.69rem;
    font-weight: 700;
    line-height: 1.15;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.plan-sidebar-adaptation-metrics {
    display: flex;
    flex-direction: column;
    gap: 0.12rem;
}

.plan-sidebar-adaptation-metric {
    font-size: 0.61rem;
    line-height: 1.2;
}

.plan-sidebar-adaptation-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    font-weight: 700;
    opacity: 0.52;
}

.plan-sidebar-adaptation-status-row {
    display: flex;
    justify-content: flex-end;
    margin-top: 0.45rem;
}

.plan-sidebar-adaptation-status {
    padding: 0.2rem 0.38rem;
    border-radius: 0.35rem;
    background: rgba(57, 169, 107, 0.14);
    font-size: 0.62rem;
    font-weight: 700;
    white-space: nowrap;
}
.plan-sidebar-empty {
    margin: 0;
    font-size: 0.78rem;
    opacity: 0.6;
}
.plan-load-legend {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-top: -0.2rem;
    margin-bottom: 0.2rem;
    font-size: 0.65rem;
    opacity: 0.72;
}

.plan-load-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    white-space: nowrap;
}

.plan-load-line {
    display: inline-block;
    width: 1.25rem;
    height: 2px;
    border-radius: 999px;
    background: currentColor;
}

.plan-load-line.planned {
    opacity: 0.65;
}

.plan-load-line.completed {
    height: 3px;
    background: #16a34a;
}

.plan-load-line.weekly {
    height: 0;
    border-top: 1px dashed currentColor;
    background: transparent;
    opacity: 0.55;
}

.plan-load-race {
    width: 0.45rem;
    height: 0.45rem;
    background: #ff4b4b;
    transform: rotate(45deg);
}
"""

def _plan_styles() -> None:
    """
    Applies visual styling to the complete plan.
    """

    st.markdown(
        """
        <style>
        .complete-plan-week {
            display: flex;
            flex-direction: column;
            width: 100%;
            gap: 0.38rem;
            padding: 0.55rem 0.65rem 0;
            box-sizing: border-box;
        }

        .complete-plan-week-spacer {
            display: block;
            width: 100%;
            height: 0.38rem;
            min-height: 0.38rem;
            flex: 0 0 0.38rem;
        }
        .complete-plan-focus {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            min-height: 2.15rem;
            padding: 0.35rem 0.55rem;
            border: 1px solid rgba(128, 128, 128, 0.17);
            border-radius: 0.5rem;
            background: rgba(128, 128, 128, 0.02);
            box-sizing: border-box;
        }

        .complete-plan-focus-label {
            flex: 0 0 auto;
            font-size: 0.64rem;
            font-weight: 750;
            text-transform: uppercase;
            opacity: 0.58;
            white-space: nowrap;
        }

        .complete-plan-focus-items {
            display: flex;
            min-width: 0;
            flex-wrap: wrap;
            gap: 0.28rem 0.7rem;
            align-items: center;
        }

        .complete-plan-focus-item {
            position: relative;
            font-size: 0.69rem;
            font-weight: 600;
            line-height: 1.2;
            white-space: nowrap;
        }

        .complete-plan-focus-item + .complete-plan-focus-item::before {
            content: "·";
            position: absolute;
            left: -0.45rem;
            opacity: 0.42;
        }

        @media (max-width: 820px) {
            .complete-plan-focus {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.25rem;
            }

            .complete-plan-focus-item {
                white-space: normal;
            }
        }
        .complete-plan-event {
            display: grid;
            grid-template-columns:
                minmax(110px, 0.8fr)
                minmax(180px, 2fr)
                auto;
            gap: 0.7rem;
            align-items: center;
            min-height: 3rem;
            padding: 0.5rem 0.65rem;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.04);
            box-sizing: border-box;
        }

        .complete-plan-event-label {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.66rem;
            font-weight: 700;
            text-transform: uppercase;
            opacity: 0.65;
            white-space: nowrap;
        }

        .complete-plan-event-icon {
            display: inline-block;
            font-size: 0.58rem;
            transform: rotate(45deg);
        }

        .complete-plan-event-title {
            min-width: 0;
            overflow: hidden;
            font-size: 0.8rem;
            font-weight: 750;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .complete-plan-event-details {
            justify-self: end;
            font-size: 0.7rem;
            font-weight: 600;
            opacity: 0.72;
            white-space: nowrap;
        }

        @media (max-width: 820px) {
            .complete-plan-event {
                grid-template-columns:
                    minmax(0, 1fr)
                    auto;
                grid-template-areas:
                    "label details"
                    "title title";
                gap: 0.25rem 0.5rem;
            }

            .complete-plan-event-label {
                grid-area: label;
            }

            .complete-plan-event-title {
                grid-area: title;
            }

            .complete-plan-event-details {
                grid-area: details;
            }
        }

        .complete-plan-session {
            position: relative;
            display: grid;
            grid-template-columns:
                3.4rem
                0.5rem
                minmax(220px, 3fr)
                minmax(62px, 0.7fr)
                minmax(62px, 0.7fr)
                minmax(90px, 0.95fr)
                minmax(76px, 0.75fr);
            gap: 0.58rem;
            align-items: center;
            min-height: 3.65rem;
            padding: 0.48rem 0.62rem;
            border: 1px solid rgba(128, 128, 128, 0.19);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.014);
            box-sizing: border-box;
        }

        .complete-plan-session:hover {
            border-color: rgba(128, 128, 128, 0.32);
            background: rgba(128, 128, 128, 0.03);
        }

        .complete-plan-session-date {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.04rem;
            line-height: 1;
        }

        .complete-plan-session-day {
            font-size: 0.61rem;
            font-weight: 750;
            letter-spacing: 0.025em;
            opacity: 0.62;
        }

        .complete-plan-session-day-number {
            font-size: 0.92rem;
            font-weight: 750;
        }

        .complete-plan-session-marker {
            display: inline-block;
            width: 0.43rem;
            height: 0.43rem;
            border-radius: 50%;
            background: #4f86f7;
        }

        .complete-plan-session-marker.quality {
            background: #ff4b4b;
        }

        .complete-plan-session-marker.race {
            border-radius: 1px;
            background: #ff4b4b;
            transform: rotate(45deg);
        }

        .complete-plan-session-main {
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 0.16rem;
        }

        .complete-plan-session-title {
            overflow: hidden;
            font-size: 0.8rem;
            font-weight: 700;
            line-height: 1.15;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .complete-plan-session-context {
            min-width: 0;
            display: flex;
            align-items: center;
            gap: 0.28rem;
            overflow: hidden;
            font-size: 0.66rem;
            line-height: 1.15;
            opacity: 0.62;
            white-space: nowrap;
        }

        .complete-plan-session-context span {
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .complete-plan-session-separator {
            flex: 0 0 auto;
        }

        .complete-plan-prescription {
            color: inherit;
        }

        .complete-plan-session-metric {
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 0.11rem;
        }

        .complete-plan-session-metric-label {
            overflow: hidden;
            font-size: 0.56rem;
            line-height: 1;
            opacity: 0.48;
            text-overflow: ellipsis;
            text-transform: uppercase;
            white-space: nowrap;
        }

        .complete-plan-session-metric-value {
            overflow: hidden;
            font-size: 0.7rem;
            font-weight: 600;
            line-height: 1.15;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .complete-plan-session-status {
            justify-self: end;
            padding: 0.21rem 0.4rem;
            border: 1px solid rgba(128, 128, 128, 0.17);
            border-radius: 999px;
            font-size: 0.61rem;
            font-weight: 700;
            line-height: 1;
            white-space: nowrap;
        }

        .complete-plan-session-status.status-equivalent {
            border-color: rgba(57, 169, 107, 0.3);
            background: rgba(57, 169, 107, 0.1);
        }

        .complete-plan-session-status.status-modified,
        .complete-plan-session-status.status-substitute {
            border-color: rgba(210, 139, 39, 0.3);
            background: rgba(210, 139, 39, 0.1);
        }

        .complete-plan-session-status.status-missed {
            border-color: rgba(224, 90, 90, 0.3);
            background: rgba(224, 90, 90, 0.1);
        }

        .complete-plan-session.status-missed {
            opacity: 0.68;
        }

        @media (max-width: 1050px) {
            .complete-plan-session {
                grid-template-columns:
                    3.2rem
                    0.5rem
                    minmax(170px, 2fr)
                    repeat(3, minmax(58px, 0.7fr))
                    minmax(70px, 0.7fr);
            }
        }

        @media (max-width: 820px) {
            .complete-plan-session {
                grid-template-columns:
                    3rem
                    0.5rem
                    minmax(0, 1fr)
                    auto;
                grid-template-areas:
                    "date marker main status"
                    "date marker metrics metrics";
                row-gap: 0.38rem;
            }

            .complete-plan-session-date {
                grid-area: date;
            }

            .complete-plan-session-marker {
                grid-area: marker;
            }

            .complete-plan-session-main {
                grid-area: main;
            }

            .complete-plan-session-status {
                grid-area: status;
            }

            .complete-plan-session-metric {
                display: inline-flex;
                flex-direction: row;
                align-items: baseline;
                gap: 0.2rem;
            }

            .complete-plan-session-metric:nth-of-type(1) {
                grid-area: metrics;
                justify-self: start;
            }

            .complete-plan-session-metric:nth-of-type(2),
            .complete-plan-session-metric:nth-of-type(3) {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
def _compact_plan_layout_styles(
    subtitle: str,
) -> None:
    """
    Balances compactness and readability on the plan page.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0 !important;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        div[data-testid="stMainBlockContainer"]
        > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        .plan-page-header {
            margin: 0 0 0.45rem 0;
            padding: 0;
        }

        .plan-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .plan-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        div[data-testid="stMainBlockContainer"] h2,
        div[data-testid="stMainBlockContainer"] h3 {
            margin-top: 0.3rem;
            margin-bottom: 0.25rem;
        }

        div[data-testid="stMainBlockContainer"] p {
            margin-top: 0.15rem;
            margin-bottom: 0.35rem;
        }

        div[data-testid="stDivider"] {
            margin-top: 0.25rem;
            margin-bottom: 0.25rem;
        }

        div[data-testid="stCaptionContainer"] {
            margin-bottom: 0.15rem;
        }

        div[data-testid="stAltairChart"] {
            margin-top: -0.45rem;
            margin-bottom: -0.45rem;
        }

        button[kind="primary"] {
            min-height: 2.45rem;
            margin-top: 0;
            white-space: nowrap;
        }

        .plan-generate-button-spacer {
            height: 1.55rem;
        }

        .plan-progression-heading {
            margin: 0.15rem 0 0.05rem 0;
        }

        .plan-progression-heading h3 {
            margin: 0;
            font-size: 1.35rem;
            line-height: 1.1;
        }

        .plan-chart-block {
            margin-top: 0;
            margin-bottom: -0.15rem;
        }

        .plan-chart-heading {
            margin: 0 0 0.05rem 0;
            font-size: 0.78rem;
            font-weight: 700;
        }

        .plan-chart-caption {
            margin: 0 0 0.05rem 0;
            font-size: 0.64rem;
            line-height: 1.2;
            opacity: 0.62;
        }

        .plan-weeks-heading {
            margin: 0.1rem 0 0.1rem 0;
            font-size: 1rem;
            font-weight: 700;
        }

        div[data-testid="stExpander"] {
            margin-bottom: 0.45rem;
            border-radius: 0.55rem;
        }

        div[data-testid="stExpander"] details {
            overflow: hidden;
            border: 1px solid rgba(128, 128, 128, 0.24);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.015);
        }

        div[data-testid="stExpander"] details summary {
            min-height: 2.15rem;
            padding: 0.35rem 0.65rem;
            font-size: 0.72rem;
            font-weight: 650;
            box-sizing: border-box;
        }

        div[data-testid="stExpander"] details summary:hover {
            background: rgba(128, 128, 128, 0.045);
        }

        div[data-testid="stExpander"] details[open] summary {
            border-bottom: 1px solid rgba(128, 128, 128, 0.16);
            background: rgba(128, 128, 128, 0.035);
        }

        div[data-testid="stExpander"] details summary:focus,
        div[data-testid="stExpander"] details summary:focus-visible {
            outline: none;
            box-shadow: none;
        }

        div[data-testid="stExpanderDetails"] {
            display: block;
            overflow: hidden;
            padding: 0;
            box-sizing: border-box;
        }

        div[data-testid="stExpander"] summary p {
            margin: 0;
            font-size: 0.72rem;
            line-height: 1.2;
        }

        div[data-testid="stExpander"] summary p:first-letter {
            color: #ff4b4b;
        }

        </style>
        """
        + (
            '<div class="plan-page-header">'
            '<div class="plan-page-title">'
            "Plan"
            "</div>"
            '<div class="plan-page-subtitle">'
            f"{escape(subtitle)}"
            "</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
def _plan_header_caption(
    plan,
) -> str:
    """
    Builds the contextual plan-page subtitle.
    """

    target_title = (
        str(
            plan.target_event_title
            or ""
        )
        .strip()
    )

    target_date = (
        plan.target_event_date
    )

    if target_title and target_date:

        return (
            f"Strategy through {target_title}"
            " · "
            f"{target_date.strftime('%d %b %Y')}"
        )

    return (
        "Review the complete persistent plan "
        "through the target event and recovery."
    )

def _ics_escape(
    value,
) -> str:
    """
    Escapes text for an iCalendar field.
    """

    return (
        str(
            value
            or ""
        )
        .replace(
            "\\",
            "\\\\",
        )
        .replace(
            ";",
            "\\;",
        )
        .replace(
            ",",
            "\\,",
        )
        .replace(
            "\r\n",
            "\\n",
        )
        .replace(
            "\n",
            "\\n",
        )
    )


def _plan_calendar_ics(
    plan,
) -> str:
    """
    Exports every planned workout as an iCalendar event.
    """

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//PerformanceLab//Training Plan//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:PerformanceLab Training Plan",
    ]

    event_index = 0

    for week in plan.weeks:

        for workout in week.workouts:

            event_index += 1

            start = (
                workout.scheduled_at
            )

            duration = (
                workout.duration
                or timedelta(
                    hours=1
                )
            )

            end = (
                start
                + duration
            )

            title = (
                workout.title
                or "Planned workout"
            )

            description_parts = []

            if workout.sport:

                description_parts.append(
                    str(
                        workout.sport
                    )
                )

            if workout.intensity:

                description_parts.append(
                    (
                        "Intensity: "
                        f"{workout.intensity}"
                    )
                )

            if workout.phase:

                description_parts.append(
                    (
                        "Phase: "
                        f"{workout.phase}"
                    )
                )

            if (
                workout.prescription_summary
            ):

                description_parts.append(
                    str(
                        workout
                        .prescription_summary
                    )
                )

            description = "\\n".join(
                _ics_escape(
                    part
                )
                for part
                in description_parts
            )

            uid = (
                f"{plan.plan_id}-"
                f"{start.strftime('%Y%m%d%H%M%S')}-"
                f"{event_index}"
                "@performancelab"
            )

            lines.extend(
                [
                    "BEGIN:VEVENT",
                    (
                        "UID:"
                        + uid
                    ),
                    (
                        "DTSTART:"
                        + start.strftime(
                            "%Y%m%dT%H%M%S"
                        )
                    ),
                    (
                        "DTEND:"
                        + end.strftime(
                            "%Y%m%dT%H%M%S"
                        )
                    ),
                    (
                        "SUMMARY:"
                        + _ics_escape(
                            title
                        )
                    ),
                    (
                        "DESCRIPTION:"
                        + description
                    ),
                    "STATUS:CONFIRMED",
                    "TRANSP:TRANSPARENT",
                    "END:VEVENT",
                ]
            )

    lines.append(
        "END:VCALENDAR"
    )

    return (
        "\r\n".join(
            lines
        )
        + "\r\n"
    )

def show_plan_page(
    athlete,
    *,
    on_generate_plan=None,
) -> None:
    """
    Displays the athlete's complete persistent plan.
    """

    today = date.today()

    plan = PlanPresenter(
        plan=athlete.training_plan,
        history=athlete.history,
    ).build(
        reference_day=today
    )

    title_column, action_column = (
        st.columns(
            [4.5, 1.5],
            gap="medium",
        )
    )

    with title_column:

        plan_subtitle = (
            _plan_header_caption(
                plan
            )
        )

        _compact_plan_layout_styles(
            plan_subtitle
        )

    with action_column:

        st.markdown(
            '<div class="plan-generate-button-spacer"></div>',
            unsafe_allow_html=True,
        )

        st.button(
            "Generate plan",
            icon=":material/auto_awesome:",
            type="primary",
            use_container_width=True,
            key="plan_generate",
            on_click=on_generate_plan,
            disabled=(
                on_generate_plan is None
            ),
        )

        calendar_data = (
            _plan_calendar_ics(
                plan
            )
            if plan.weeks
            else ""
        )

        st.download_button(
            "Export calendar",
            data=calendar_data,
            file_name=(
                "performancelab-plan.ics"
            ),
            mime=(
                "text/calendar; "
                "charset=utf-8"
            ),
            use_container_width=True,
            disabled=(
                not bool(
                    plan.weeks
                )
            ),
        )

    if not plan.weeks:

        st.info(
            "No training plan is available. "
            "Generate a plan to begin."
        )

        return

    summary = (
        _plan_summary_metrics(
            plan
        )
    )

    current_week = (
        _current_plan_week(
            plan.weeks,
            reference_day=today,
        )
    )

    main_column, sidebar_column = (
        st.columns(
            [3.4, 1],
            gap="medium",
        )
    )

    with main_column:

        timeline_visible_start = (
            current_week.start_date
            if current_week is not None
            else today
        )

        timeline_visible_end = (
            current_week.end_date
            if current_week is not None
            else today
        )

        timeline_html = (
            phase_timeline_from_phases_html(
                phases=plan.phases,
                current_date=today,
                visible_start=(
                    timeline_visible_start
                ),
                visible_end=(
                    timeline_visible_end
                ),
            )
        )

        if timeline_html:

            st.markdown(
                (
                    "<style>"
                    + phase_timeline_styles()
                    + "</style>"
                    + timeline_html
                ),
                unsafe_allow_html=True,
            )

        summary_html = (
            summary_cards_html(
                (
                    (
                        "calendar_month",
                        "Horizon",
                        summary["Horizon"],
                    ),
                    (
                        "monitoring",
                        "Planned load",
                        summary["Planned load"],
                    ),
                    (
                        "route",
                        "Max distance",
                        summary["Max distance"],
                    ),
                    (
                        "terrain",
                        "Max elevation",
                        summary["Max elevation"],
                    ),
                )
            )
        )

        st.markdown(
            (
                "<style>"
                + summary_cards_styles()
                + "</style>"
                + summary_html
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="plan-progression-heading">'
                "<h3>Plan progression</h3>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                '<div class="plan-chart-block">'
                '<div class="plan-chart-heading">'
                "Planned load"
                "</div>"
                '<div class="plan-chart-caption">'
                "Session load · dashed line shows weekly total."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.altair_chart(
            _planned_load_chart(
                plan
            ),
            use_container_width=True,
        )
        st.html(
            _plan_load_legend_html()
        )
        st.markdown(
            (
                '<div class="plan-chart-block">'
                '<div class="plan-chart-heading">'
                "Distance and elevation"
                "</div>"
                '<div class="plan-chart-caption">'
                "Weekly totals · diamonds mark races."
                "</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        st.altair_chart(
            _distance_elevation_chart(
                plan
            ),
            use_container_width=True,
        )

        st.markdown(
            (
                '<div class="plan-weeks-heading">'
                "Plan weeks"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

        _plan_styles()

        for week in plan.weeks:

            label = (
                _week_summary_label(
                    week,
                    reference_day=today,
                )
            )

            with st.expander(
                label,
                expanded=False,
            ):

                st.markdown(
                    _week_html(
                        week
                    ),
                    unsafe_allow_html=True,
                )
                
    with sidebar_column:

        sidebar_html = (
            '<div class="plan-sidebar-stack">'
            + _sidebar_phase_html(
                plan.current_phase
            )
            + _sidebar_week_html(
                current_week
            )
            + _sidebar_adaptation_html(
                plan.latest_adaptation,
                reference_day=plan.reference_day,
            )
            + "</div>"
        )

        st.markdown(
            (
                "<style>"
                + _sidebar_styles()
                + "</style>"
                + sidebar_html
            ),
            unsafe_allow_html=True,
        )