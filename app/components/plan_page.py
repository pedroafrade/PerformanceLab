"""
PerformanceLab

Complete training-plan page.
"""

from datetime import date, timedelta
from html import escape
from pathlib import Path

from dataclasses import replace

import altair as alt
import streamlit as st
import streamlit.components.v1 as components

from streamlit_sortables import (
    sort_items,
)

from performancelab.presentation import (
    CalendarPresenter,
    PlanGenerationNoticePresenter,
    PlanPresenter,
)
from performancelab.training.planning.planned_workout import (
    format_planned_duration_minutes,
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
from .upcoming_events import (
    upcoming_events_html,
    upcoming_events_styles,
)
from performancelab.training.planning import (
    PlanBuilderDraft,
)
from performancelab.training.load import (
    planned_workout_load,
)

_plan_builder_board_component = components.declare_component(
    "plan_builder_board",
    path=str(Path(__file__).with_name("plan_builder_board")),
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
                "Duration label": (
                    format_planned_duration_minutes(
                        duration_minutes
                    )
                    if duration_minutes is not None
                    else "—"
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

def _actual_and_adapted_load_chart_data(
    plan,
) -> list[dict]:
    """Joins completed history to the remaining adapted plan."""

    rows = [
        {
            "Date": point.day.isoformat(),
            "Session": point.title,
            "Actual or adapted load": float(
                point.completed_load
            ),
            "Source": "Completed",
        }
        for point in plan.completed_load_points
    ]

    completed_days = {
        point.day
        for point in plan.completed_load_points
    }

    rows.extend(
        {
            "Date": point.day.isoformat(),
            "Session": point.title,
            "Actual or adapted load": float(
                point.planned_load
            ),
            "Source": "Adapted projection",
        }
        for point in plan.chart_points
        if (
            point.planned_load is not None
            and not point.is_race
            and point.day >= plan.reference_day
            and point.day not in completed_days
        )
    )

    return sorted(
        rows,
        key=lambda row: (
            row["Date"],
            row["Source"],
            row["Session"],
        ),
    )

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
        getattr(
            plan,
            "original_chart_points",
            plan.chart_points,
        )
    )

    weekly_load_data = (
        _weekly_planned_load_curve_data(
            getattr(
                plan,
                "original_chart_points",
                plan.chart_points,
            )
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
                    "Duration label:N",
                    title="Duration",
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
            color="#60a5fa",
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
            color="#60a5fa",
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
        _actual_and_adapted_load_chart_data(
            plan
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
                    "Actual or adapted load:Q",
                    title="Load (AU)",
                    format=".0f",
                ),
                alt.Tooltip(
                    "Source:N",
                    title="Source",
                ),
            ],
        )
    )

    completed_line = (
        completed_base
        .transform_filter(
            alt.datum.Source
            == "Completed"
        )
        .mark_line(
            interpolate="linear",
            strokeWidth=2.4,
            color="#16a34a",
        )
        .encode(
            y=alt.Y(
                "Actual or adapted load:Q",
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
        .transform_filter(
            alt.datum.Source
            == "Completed"
        )
        .mark_point(
            filled=True,
            size=64,
            color="#16a34a",
            stroke="white",
            strokeWidth=0.6,
        )
        .encode(
            y=alt.Y(
                "Actual or adapted load:Q",
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

    adapted_projection_line = (
        completed_base
        .transform_filter(
            alt.datum.Source
            == "Adapted projection"
        )
        .mark_line(
            interpolate="linear",
            strokeWidth=2.6,
            strokeDash=[
                6,
                4,
            ],
            color="#16a34a",
            opacity=0.9,
        )
        .encode(
            y=alt.Y(
                "Actual or adapted load:Q",
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

    adapted_projection_points = (
        completed_base
        .transform_filter(
            alt.datum.Source
            == "Adapted projection"
        )
        .mark_point(
            filled=False,
            size=68,
            color="#16a34a",
            strokeWidth=1.5,
            opacity=0.9,
        )
        .encode(
            y=alt.Y(
                "Actual or adapted load:Q",
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
                    "Duration label:N",
                    title="Duration",
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
            adapted_projection_line,
            adapted_projection_points,
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
            Original plan
        </span>
        <span class="plan-load-legend-item">
            <span class="plan-load-line completed"></span>
            Completed
        </span>
        <span class="plan-load-legend-item">
            <span class="plan-load-line projection"></span>
            Adapted projection
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
def _stimulus_suggestion_html(
    suggestion,
) -> str:
    """
    Builds a transparent before/after stimulus adaptation.
    """

    if suggestion is None:
        return ""

    missing_label = (
        str(
            suggestion.missing_stimulus
        )
        .replace("_", " ")
        .title()
    )

    completed_label = (
        str(
            suggestion.completed_stimulus
        )
        .replace("_", " ")
        .title()
    )

    candidate_label = (
        str(
            suggestion.candidate_stimulus
        )
        .replace("_", " ")
        .title()
    )

    is_applied = bool(
        getattr(
            suggestion,
            "applied",
            False,
        )
    )

    status_label = (
        "Applied"
        if is_applied
        else "Suggested"
    )

    adjusted_titles = {
        "hills": "Hill Reps",
        "threshold": "LT2 Run",
        "tempo": "Tempo Run",
        "vo2max": "VO2max Intervals",
        "speed": "Speed Reps",
    }

    stimulus_key = (
        str(
            suggestion.missing_stimulus
        )
        .strip()
        .lower()
    )

    adjusted_title = (
        adjusted_titles.get(
            stimulus_key,
            missing_label,
        )
    )

    if (
        str(
            suggestion.completed_stimulus
        ).strip().lower()
        == "unknown"
    ):
        gap_html = (
            "<span>Planned stimulus not completed</span>"
            "<span>·</span>"
            "<strong>Missed session</strong>"
        )
    else:
        gap_html = (
            f"<span>{escape(missing_label)} planned</span>"
            "<span>→</span>"
            f"<span>{escape(completed_label)} completed</span>"
        )

    planned_html = (
        _sidebar_adaptation_column_html(
            label="Planned session",
            title=(
                suggestion
                .candidate_workout_title
            ),
            rows=(
                candidate_label,
                (
                    suggestion
                    .candidate_workout_day
                    .strftime("%d %b")
                ),
            ),
            adjusted=False,
        )
    )

    adjusted_html = (
        _sidebar_adaptation_column_html(
            label=(
                "Adjusted session"
                if is_applied
                else "Proposed session"
            ),
            title=adjusted_title,
            rows=(
                missing_label,
                (
                    suggestion
                    .candidate_workout_day
                    .strftime("%d %b")
                ),
            ),
            adjusted=True,
        )
    )

    note = (
        "The session type and prescription were updated "
        "without adding another demanding training day."
        if is_applied
        else (
            "No session type has been changed. Athlete "
            "confirmation is required."
        )
    )

    return (
        '<div class="plan-stimulus-suggestion">'
        '<div class="plan-stimulus-suggestion-header">'
        "<span>Stimulus rebalancing</span>"
        '<span class="plan-stimulus-suggestion-status">'
        f"{escape(status_label)}"
        "</span>"
        "</div>"

        '<div class="plan-stimulus-suggestion-summary">'
        '<div class="plan-stimulus-suggestion-source">'
        f"<strong>{escape(suggestion.source_workout_title)}</strong>"
        f" · {suggestion.source_workout_day:%d %b}"
        "</div>"
        '<div class="plan-stimulus-suggestion-gap">'
        f"{gap_html}"
        "</div>"
        "</div>"

        '<div class="plan-sidebar-adaptation-comparison '
        'plan-stimulus-suggestion-comparison">'
        f"{planned_html}"
        '<div class="plan-sidebar-adaptation-arrow">'
        "→"
        "</div>"
        f"{adjusted_html}"
        "</div>"

        '<div class="plan-stimulus-suggestion-explanation">'
        '<p class="plan-stimulus-suggestion-recommendation">'
        f"{escape(suggestion.recommendation)}"
        "</p>"
        '<p class="plan-stimulus-suggestion-rationale">'
        f"{escape(suggestion.rationale)}"
        "</p>"
        '<p class="plan-stimulus-suggestion-note">'
        f"{escape(note)}"
        "</p>"
        "</div>"
        "</div>"
    )

def _sidebar_adaptation_html(
    adaptation,
    *,
    reference_day: date,
    show_heading: bool = True,
    stimulus_suggestion=None,
) -> str:
    """
    Builds the latest-adaptation sidebar card.
    """

    heading_html = (
        '<div class="plan-sidebar-heading">'
        '<span class="plan-sidebar-icon">↻</span>'
        "<span>Plan adaptation</span>"
        "</div>"
        if show_heading
        else ""
    )
    suggestion_html = (
        _stimulus_suggestion_html(
            stimulus_suggestion
        )
    )

    if suggestion_html:

        return (
            '<section class="plan-sidebar-card '
            'plan-sidebar-adaptation-card">'
            f"{heading_html}"
            f"{suggestion_html}"
            "</section>"
        )

    if adaptation is None:

        return (
            '<section class="plan-sidebar-card '
            'plan-sidebar-adaptation-card">'
            f"{heading_html}"
            '<p class="plan-stimulus-suggestion-empty">'
            "No pending stimulus rebalancing suggestion."
            "</p>"
            '<p class="plan-sidebar-empty">'
            "No adaptations or suggestions yet."
            "</p>"
            "</section>"
        )

    date_label = (
        "Session date · "
        f"{adaptation.workout_day:%d %b %Y}"
    )

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
        f"{heading_html}"
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
    background: #60a5fa;
}

.plan-load-line.completed {
    height: 3px;
    background: #16a34a;
}

.plan-load-line.projection {
    height: 0;
    border-top: 2px dashed #16a34a;
    background: transparent;
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

        /* Scope sizing to Plan; never change the application sidebar. */
        @media (min-width: 1100px) {
            section[data-testid="stMain"] {
                overflow-y: hidden;
            }
            .st-key-plan_lower_row
            > div[data-testid="stVerticalBlock"] {
                gap: 0;
            }

            .st-key-plan_lower_row
            [data-testid="stHorizontalBlock"] {
                align-items: stretch;
            }

            .st-key-plan_lower_row
            [data-testid="stColumn"]
            > div[data-testid="stVerticalBlock"] {
                height: 100%;
            }

            .st-key-plan_weeks_section,
            .st-key-plan_latest_adaptation {
                display: flex;
                height: 100%;
                flex-direction: column;
            }

            .st-key-plan_latest_adaptation
            [data-testid="stHtml"] {
                display: flex;
                flex: 1 1 auto;
                min-height: 0;
            }

            .st-key-plan_latest_adaptation
            .plan-sidebar-card {
                width: 100%;
                height: 220px;
                min-height: 0;
                padding-bottom: 0.75rem;
                overflow-x: hidden !important;
                overflow-y: auto !important;
                box-sizing: border-box;
            }
            .st-key-plan_page_columns [data-testid="stHorizontalBlock"]:has(.st-key-plan_weeks_scroll) {
                align-items: stretch;
            }
            .st-key-plan_page_columns [data-testid="stHorizontalBlock"]:has(.st-key-plan_weeks_scroll)
            > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] {
                height: 100%;
                gap: 0.4rem;
            }
            .st-key-plan_page_columns [data-testid="stLayoutWrapper"] {
                flex-shrink: 0;
            }
            .st-key-plan_weeks_scroll {
                height: clamp(8rem, calc(100dvh - 46rem), 16rem) !important;
                min-height: 8rem;
                overflow-y: auto;
                scrollbar-gutter: stable;
            }
            .st-key-plan_page_columns [data-testid="stLayoutWrapper"]:has(> .st-key-plan_weeks_section) {
                margin-top: -0.5rem;
            }
            .st-key-plan_page_columns [data-testid="stLayoutWrapper"]:has(> .st-key-plan_summary_cards),
            .st-key-plan_summary_cards,
            .st-key-plan_summary_cards [data-testid="stElementContainer"],
            .st-key-plan_summary_cards [data-testid="stHtml"] {
                display: flex;
                flex-direction: column;
                flex: 1 0 auto;
            }
            .st-key-plan_summary_cards .plan-sidebar-stack {
                height: auto;
                flex: 0 0 auto;
                gap: 0.5rem;
                justify-content: flex-start;
            }
            .st-key-plan_summary_cards
            .plan-sidebar-card {
                flex-shrink: 0;
                padding: 0.65rem;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child {
                display: flex;
                min-height: 0;
                margin-top: 0;
                overflow: hidden;
                flex: 1 1 0;
                flex-direction: column;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child
            .upcoming-events {
                min-height: 0;
                padding-right: 0.2rem;
                overflow-y: auto;
                scrollbar-gutter: stable;
                flex: 1 1 auto;
            }
            .st-key-plan_summary_cards .plan-sidebar-heading { margin-bottom: 0.45rem; }
            .st-key-plan_summary_cards .plan-sidebar-phase-name { font-size: 1.35rem; margin-bottom: 0.25rem; }
            .st-key-plan_summary_cards .plan-sidebar-date-range,
            .st-key-plan_summary_cards .plan-sidebar-week-phase,
            .st-key-plan_summary_cards .plan-sidebar-week-summary { margin-bottom: 0.4rem; }
            .st-key-plan_summary_cards .plan-sidebar-divider { margin: 0.45rem 0; }
            .st-key-plan_summary_cards .plan-sidebar-phase-metrics { gap: 0.3rem; }
            .st-key-plan_summary_cards .plan-sidebar-phase-metric { padding: 0.3rem 0.4rem; }
            .st-key-plan_summary_cards .plan-sidebar-week-range { font-size: 1.15rem; }
            .st-key-plan_summary_cards .plan-sidebar-session { min-height: 1.75rem; padding: 0.25rem 0.4rem; }
            .st-key-plan_summary_cards .plan-sidebar-adaptation-context { margin-bottom: 0.4rem; }
            .st-key-plan_summary_cards .plan-sidebar-adaptation-column { padding: 0.35rem; }
            /*
             * Align Plan Weeks, Latest Adaptation and
             * Upcoming Events against the same lower edge.
             */
            .st-key-plan_lower_row {
                display: flex;
                min-height: 0;
                flex: 1 1 auto;
            }

            .st-key-plan_lower_row
            > div[data-testid="stVerticalBlock"],
            .st-key-plan_lower_row
            [data-testid="stHorizontalBlock"],
            .st-key-plan_lower_row
            [data-testid="stColumn"] {
                min-height: 0;
                height: 100%;
            }

            .st-key-plan_lower_row
            [data-testid="stColumn"]
            > div[data-testid="stVerticalBlock"] {
                display: flex;
                min-height: 0;
                height: 100%;
                gap: 0.35rem;
                flex-direction: column;
            }

            .st-key-plan_weeks_section,
            .st-key-plan_latest_adaptation {
                display: flex;
                min-height: 0;
                height: 100%;
                flex: 1 1 auto;
                flex-direction: column;
            }

            .st-key-plan_weeks_section
            > div[data-testid="stVerticalBlock"],
            .st-key-plan_latest_adaptation
            > div[data-testid="stVerticalBlock"] {
                display: flex;
                min-height: 0;
                height: 100%;
                gap: 0.35rem;
                flex-direction: column;
            }

            .st-key-plan_weeks_section
            .plan-weeks-heading,
            .st-key-plan_latest_adaptation
            .plan-weeks-heading {
                display: flex;
                align-items: center;
                min-height: 1.25rem;
                margin: 0 !important;
                padding: 0;
                line-height: 1.25rem;
                flex: 0 0 1.25rem;
            }

            .st-key-plan_weeks_section
            div[data-testid="stElementContainer"]:has(
                > .st-key-plan_weeks_scroll
            ),
            .st-key-plan_latest_adaptation
            div[data-testid="stElementContainer"]:has(
                > div[data-testid="stHtml"]
            ) {
                display: flex;
                min-height: 0;
                flex: 1 1 auto;
            }

            .st-key-plan_lower_row
            .st-key-plan_weeks_scroll {
                width: 100%;
                min-height: 220px;
                height: auto !important;
                flex: 1 1 auto;
            }

            .st-key-plan_latest_adaptation
            div[data-testid="stHtml"],
            .st-key-plan_latest_adaptation
            .plan-sidebar-card {
                width: 100%;
                min-height: 220px;
                height: auto;
                flex: 1 1 auto;
                box-sizing: border-box;
            }

            .st-key-plan_summary_cards,
            .st-key-plan_summary_cards
            div[data-testid="stHtml"],
            .st-key-plan_summary_cards
            .plan-sidebar-stack {
                min-height: 0;
                height: 100%;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child {
                min-height: 0;
                flex: 1 1 auto;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child
            .upcoming-events {
                min-height: 0;
                overflow-y: auto;
                flex: 1 1 auto;
            }
            /*
             * Final alignment of the three lower Plan
             * containers.
             */
            .st-key-plan_latest_adaptation {
                transform: translateY(-0.4rem);
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child {
                height:
                    calc(
                        clamp(
                            8rem,
                            calc(100dvh - 46rem),
                            16rem
                        )
                        + 1.6rem
                    );
                min-height: 0;
                max-height:
                    calc(
                        clamp(
                            8rem,
                            calc(100dvh - 46rem),
                            16rem
                        )
                        + 1.6rem
                    );
                margin-top: 0.4rem;
                overflow: hidden;
                flex:
                    0 0
                    calc(
                        clamp(
                            8rem,
                            calc(100dvh - 46rem),
                            16rem
                        )
                        + 1.6rem
                    );
                box-sizing: border-box;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child
            .upcoming-events {
                min-height: 0;
                max-height: 100%;
                overflow-x: hidden;
                overflow-y: auto;
                flex: 1 1 auto;
                scrollbar-gutter: stable;
            }
        }
        @media (max-width: 1099px) {
            .st-key-plan_latest_adaptation
            .plan-sidebar-card {
                height: auto;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child,
            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child
            .upcoming-events {
                height: auto;
                max-height: none;
                overflow: visible;
            }
            .st-key-plan_weeks_scroll {
                height: auto !important;
                max-height: none !important;
                overflow: visible !important;
            }
            .st-key-plan_lower_row,
            .st-key-plan_lower_row
            [data-testid="stHorizontalBlock"],
            .st-key-plan_lower_row
            [data-testid="stColumn"],
            .st-key-plan_weeks_section,
            .st-key-plan_latest_adaptation {
                display: block;
                min-height: 0;
                height: auto;
            }

            .st-key-plan_latest_adaptation
            .plan-sidebar-card {
                min-height: 0;
                height: auto;
            }
            .st-key-plan_latest_adaptation {
                transform: none;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child {
                height: auto;
                min-height: 0;
                max-height: none;
                margin-top: 0;
                overflow: visible;
                flex: none;
            }
        }

        .plan-overview {
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }
        .plan-overview > * { flex-shrink: 0; }
        .plan-overview .weekly-phase-timeline { margin: 0; }

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

        section[data-testid="stMain"] div[data-testid="stDivider"] {
            margin-top: 0.25rem;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stMain"] div[data-testid="stCaptionContainer"] {
            margin-bottom: 0.15rem;
        }

        section[data-testid="stMain"] div[data-testid="stAltairChart"] {
            margin-top: -0.45rem;
            margin-bottom: -0.45rem;
        }

        section[data-testid="stMain"] .st-key-plan_generate button {
            min-height: 2.45rem;
            margin-top: 0;
            white-space: nowrap;
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

        section[data-testid="stMain"] div[data-testid="stExpander"] {
            margin-bottom: 0.45rem;
            border-radius: 0.55rem;
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] details {
            overflow: hidden;
            border: 1px solid rgba(128, 128, 128, 0.24);
            border-radius: 0.55rem;
            background: rgba(128, 128, 128, 0.015);
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] details summary {
            min-height: 2.15rem;
            padding: 0.35rem 0.65rem;
            font-size: 0.72rem;
            font-weight: 650;
            box-sizing: border-box;
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] details summary:hover {
            background: rgba(128, 128, 128, 0.045);
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] details[open] summary {
            border-bottom: 1px solid rgba(128, 128, 128, 0.16);
            background: rgba(128, 128, 128, 0.035);
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] details summary:focus,
        section[data-testid="stMain"] div[data-testid="stExpander"] details summary:focus-visible {
            outline: none;
            box-shadow: none;
        }

        section[data-testid="stMain"] div[data-testid="stExpanderDetails"] {
            display: block;
            overflow: hidden;
            padding: 0;
            box-sizing: border-box;
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] summary p {
            margin: 0;
            font-size: 0.72rem;
            line-height: 1.2;
        }

        section[data-testid="stMain"] div[data-testid="stExpander"] summary p:first-letter {
            color: #ff4b4b;
        }
        /*
         * The three lower cards share one Streamlit row.
         * These final rules supersede the former
         * cross-column alignment adjustments.
         */
        @media (min-width: 1100px) {
            .st-key-plan_lower_row
            [data-testid="stHorizontalBlock"] {
                align-items: stretch;
            }

            .st-key-plan_lower_row
            [data-testid="stColumn"]
            > div[data-testid="stVerticalBlock"] {
                display: flex;
                height: 100%;
                gap: 0.35rem;
                flex-direction: column;
            }

            .st-key-plan_weeks_section,
            .st-key-plan_latest_adaptation,
            .st-key-plan_upcoming_events {
                display: flex;
                height: 100%;
                flex-direction: column;
            }

            .st-key-plan_weeks_section
            > div[data-testid="stVerticalBlock"],
            .st-key-plan_latest_adaptation
            > div[data-testid="stVerticalBlock"],
            .st-key-plan_upcoming_events
            > div[data-testid="stVerticalBlock"] {
                display: flex;
                height: 100%;
                gap: 0.35rem;
                flex-direction: column;
            }

            .st-key-plan_lower_row
            .plan-weeks-heading {
                display: flex;
                align-items: center;
                min-height: 1.25rem;
                height: 1.25rem;
                margin: 0 !important;
                padding: 0;
                line-height: 1.25rem;
                flex: 0 0 1.25rem;
            }

            .st-key-plan_lower_row {
                position: relative;
                z-index: 1;
                margin-top: -2.5rem;
                margin-bottom: -1rem;
            }

            .st-key-plan_lower_row
            .st-key-plan_weeks_scroll,
            .st-key-plan_latest_adaptation
            .plan-sidebar-card,
            .st-key-plan_upcoming_events
            .plan-upcoming-events-card {
                width: 100%;
                min-height: 8rem;
                height:
                    clamp(
                        8rem,
                        calc(100dvh - 46rem),
                        13.75rem
                    ) !important;
                max-height:
                    clamp(
                        8rem,
                        calc(100dvh - 46rem),
                        13.75rem
                    );
                margin: 0;
                overflow: hidden;
                box-sizing: border-box;
            }

            .st-key-plan_lower_row
            .st-key-plan_weeks_scroll {
                overflow-y: auto;
                scrollbar-gutter: stable;
            }

            .st-key-plan_latest_adaptation {
                transform: none;
            }

            .st-key-plan_upcoming_events
            .plan-upcoming-events-card {
                display: flex;
                min-height: 8rem;
                padding: 0.65rem;
                overflow: hidden;
                flex-direction: column;
            }

            .st-key-plan_upcoming_events
            .upcoming-events {
                min-height: 0;
                padding-right: 0.2rem;
                overflow-x: hidden;
                overflow-y: auto;
                scrollbar-gutter: stable;
                flex: 1 1 auto;
            }

            .st-key-plan_page_columns
            [data-testid="stLayoutWrapper"]:has(
                > .st-key-plan_summary_cards
            ),
            .st-key-plan_summary_cards,
            .st-key-plan_summary_cards
            [data-testid="stElementContainer"],
            .st-key-plan_summary_cards
            [data-testid="stHtml"],
            .st-key-plan_summary_cards
            .plan-sidebar-stack {
                height: auto;
                min-height: 0;
                flex: 0 0 auto;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-stack {
                justify-content: flex-start;
            }

            .st-key-plan_summary_cards
            .plan-sidebar-card:last-child {
                display: block;
                height: auto;
                min-height: 0;
                max-height: none;
                margin-top: 0;
                overflow: visible;
                flex: none;
            }
        }

        @media (max-width: 1099px) {
            section[data-testid="stMain"] {
                overflow-y: auto;
            }
            .st-key-plan_lower_row {
                position: static;
                margin-top: 0;
                margin-bottom: 0;
            }

            .st-key-plan_upcoming_events
            .plan-upcoming-events-card {
                height: auto !important;
                min-height: 0;
                max-height: none;
                overflow: visible;
            }

            .st-key-plan_upcoming_events
            .upcoming-events {
                overflow: visible;
            }
        }
        .plan-adaptation-heading {
            position: relative;
            justify-content: space-between;
            overflow: visible;
        }

        .plan-adaptation-help {
            position: relative;
            margin-left: auto;
            font-size: 0.75rem;
            font-weight: 400;
            line-height: 1;
        }

        .plan-adaptation-help summary {
            display: flex;
            width: 1.25rem;
            height: 1.25rem;
            align-items: center;
            justify-content: center;
            padding: 0;
            border: 1px solid rgba(128, 128, 128, 0.5);
            border-radius: 50%;
            cursor: pointer;
            list-style: none;
            box-sizing: border-box;
        }

        .plan-adaptation-help summary::-webkit-details-marker {
            display: none;
        }

        .plan-adaptation-help summary:hover,
        .plan-adaptation-help summary:focus-visible {
            border-color: #ff4b4b;
            color: #ff4b4b;
            outline: none;
        }

        .plan-adaptation-help-panel {
            position: absolute;
            z-index: 20;
            right: 0;
            bottom: 1.6rem;
            width: min(25rem, 75vw);
            max-height: 20rem;
            padding: 0.85rem;
            border: 1px solid rgba(128, 128, 128, 0.38);
            border-radius: 0.65rem;
            background: rgb(14, 17, 23);
            color: rgb(250, 250, 250);
            box-shadow: 0 0.75rem 2rem rgba(0, 0, 0, 0.3);
            overflow-y: auto;
            font-size: 0.72rem;
            font-weight: 400;
            line-height: 1.4;
        }

        .plan-adaptation-help-panel strong {
            display: block;
            margin-bottom: 0.55rem;
            font-size: 0.78rem;
        }

        .plan-adaptation-help-panel p {
            margin: 0 0 0.55rem 0 !important;
        }

        .plan-adaptation-help-panel p:last-child {
            margin-bottom: 0 !important;
        }

        @media (prefers-color-scheme: light) {
            .plan-adaptation-help-panel {
                background: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
            }
        }
        .plan-sidebar-adaptation-card {
            min-height: 0;
            overflow-x: hidden !important;
            overflow-y: auto !important;
            scrollbar-gutter: stable;
            overscroll-behavior: contain;
        }

        .plan-stimulus-suggestion {
            margin: 0;
            padding: 0;
            border: 0;
            border-radius: 0;
            background: transparent;
        }

        .plan-stimulus-suggestion-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            font-size: 0.72rem;
            font-weight: 700;
        }

        .plan-stimulus-suggestion-status {
            padding: 0.15rem 0.4rem;
            border-radius: 999px;
            background: rgba(57, 169, 107, 0.12);
            color: #39a96b;
            font-size: 0.58rem;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .plan-stimulus-suggestion-summary {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 0.6rem;
        }

        .plan-stimulus-suggestion-source {
            min-width: 0;
            margin: 0;
            font-size: 0.68rem;
            white-space: nowrap;
        }

        .plan-stimulus-suggestion-gap {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 0.35rem;
            min-width: 0;
            margin: 0;
            font-size: 0.65rem;
            line-height: 1.25;
            text-align: right;
            opacity: 0.82;
        }

        .plan-stimulus-suggestion-comparison {
            margin-bottom: 0.65rem;
        }

        .plan-stimulus-suggestion-explanation {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
        }

        .plan-stimulus-suggestion-recommendation,
        .plan-stimulus-suggestion-rationale,
        .plan-stimulus-suggestion-note {
            margin: 0 !important;
            font-size: 0.64rem;
            line-height: 1.4;
        }

        .plan-stimulus-suggestion-recommendation {
            font-weight: 650;
        }

        .plan-stimulus-suggestion-rationale {
            opacity: 0.75;
        }

        .plan-stimulus-suggestion-note {
            opacity: 0.62;
        }

        @media (max-width: 700px) {
            .plan-stimulus-suggestion-summary {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.25rem;
            }

            .plan-stimulus-suggestion-gap {
                justify-content: flex-start;
                text-align: left;
            }
        }

        .plan-stimulus-suggestion-recommendation {
            font-weight: 650;
        }

        .plan-stimulus-suggestion-rationale {
            opacity: 0.75;
        }

        .plan-stimulus-suggestion-note {
            margin-bottom: 0 !important;
            opacity: 0.62;
        }
        .plan-stimulus-suggestion-empty {
            margin: 0 0 0.55rem 0 !important;
            padding: 0.4rem 0.5rem;
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 0.4rem;
            font-size: 0.62rem;
            line-height: 1.3;
            opacity: 0.66;
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

def _plan_generation_notice_html(
    notice,
) -> str:
    """
    Builds a compact monochrome plan-horizon summary.
    """

    rows = []

    if notice.primary_event_name:
        rows.extend(
            [
                (
                    "Primary event",
                    notice.primary_event_name,
                ),
                (
                    "Race date",
                    notice.primary_event_date.strftime(
                        "%d %B %Y"
                    ),
                ),
                (
                    "Plan ends",
                    notice.plan_end_date.strftime(
                        "%d %B %Y"
                    ),
                ),
                (
                    "Recovery",
                    (
                        f"{notice.recovery_days} "
                        "days after the race"
                    ),
                ),
            ]
        )
    else:
        rows.append(
            (
                "Plan ends",
                notice.plan_end_date.strftime(
                    "%d %B %Y"
                ),
            )
        )

    rows_html = "".join(
        (
            '<div class="plan-generation-row">'
            '<span class="plan-generation-label">'
            f"{escape(label)}"
            "</span>"
            '<span class="plan-generation-value">'
            f"{escape(value)}"
            "</span>"
            "</div>"
        )
        for label, value in rows
    )

    later_cycle_html = ""

    if notice.later_block_message:
        later_cycle_html = (
            '<div class="plan-generation-later">'
            '<div class="plan-generation-section-title">'
            "Later competition cycle"
            "</div>"
            '<p class="plan-generation-copy">'
            f"{escape(notice.later_block_message)}"
            "</p>"
            '<p class="plan-generation-note">'
            "Later events remain registered and can guide "
            "the next training cycle."
            "</p>"
            "</div>"
        )

    return (
        '<div class="plan-generation-notice">'
        '<p class="plan-generation-intro">'
        "Generating a new plan will replace the current "
        "persistent training plan."
        "</p>"
        '<div class="plan-generation-section-title">'
        "Plan horizon"
        "</div>"
        '<div class="plan-generation-facts">'
        f"{rows_html}"
        "</div>"
        f"{later_cycle_html}"
        "</div>"
    )

def _plan_builder_workspace_html(plan) -> str:
    """Builds the weekly structure below the shared load chart."""
    weeks = tuple(plan.weeks)
    if not weeks:
        return '<p class="plan-builder-empty">Generate a plan to populate the timeline.</p>'

    cards = []
    titles = []
    for week in weeks:
        sessions = []
        for workout in week.workouts:
            title = workout.title or "Rest day"
            if workout.title and title not in titles:
                titles.append(title)
            sessions.append(
                f'<div><span>{workout.scheduled_at:%a %d}</span>'
                f'<strong>{escape(title)}</strong></div>'
            )
        cards.append(
            f'<article><header>{week.start_date:%d %b} – {week.end_date:%d %b}</header>'
            + "".join(sessions) + '</article>'
        )
    library = "".join(f'<span>{escape(title)}</span>' for title in titles)
    return (
        '<section class="plan-builder-workspace">'
        '<h4>Plan structure by week</h4>'
        f'<div class="plan-builder-weeks">{"".join(cards)}</div>'
        '<h4>Session library</h4>'
        f'<div class="plan-builder-library">{library}</div></section>'
    )

def _plan_builder_session_marker(
    title: str | None,
) -> str:
    """
    Returns the Calendar colour marker for a session type.
    """

    normalized = str(
        title or ""
    ).strip().lower()

    if any(
        value in normalized
        for value in (
            "race",
            "trail pé firme",
        )
    ):
        return "🟥"

    if any(
        value in normalized
        for value in (
            "hill",
            "hills",
        )
    ):
        return "🟩"

    if any(
        value in normalized
        for value in (
            "tempo",
            "lt2",
            "threshold",
            "interval",
        )
    ):
        return "🟨"

    if "long" in normalized:
        return "🟪"

    if any(
        value in normalized
        for value in (
            "easy",
            "recovery",
            "shakeout",
        )
    ):
        return "🟢"

    return "⬜"

def _plan_builder_workout_token(
    workout,
    *,
    index: int,
) -> str:
    """
    Returns a unique label without displaying its identifier.
    """

    marker = (
        _plan_builder_session_marker(
            workout.title
        )
    )

    identifier = workout.planned_workout_id
    invisible_identifier = "".join(
        "\u200b" if bit == "0" else "\u200c"
        for character in identifier.encode("utf-8")
        for bit in f"{character:08b}"
    )

    return (
        f"{marker} "
        f"{workout.title or 'Planned workout'}"
        f"{invisible_identifier}"
    )


def _show_plan_builder_drag_board(
    *,
    draft,
    draft_key: str,
    plan_start: date,
    plan_end: date,
    reference_day: date,
):
    """
    Displays the plan as seven-day columns.

    Returns the possibly revised draft and feedback without
    forcing a page rerun, keeping Plan Builder open.
    """

    workouts = tuple(
        sorted(
            draft.workouts,
            key=lambda workout: (
                workout.scheduled_at
            ),
        )
    )

    if (
        plan_start is None
        or plan_end is None
        or plan_end < plan_start
    ):
        st.info(
            "A valid plan horizon is required "
            "before editing sessions."
        )

        return draft

    grid_start = (
        plan_start
        - timedelta(
            days=plan_start.weekday()
        )
    )

    grid_end = (
        plan_end
        + timedelta(
            days=(
                6
                - plan_end.weekday()
            )
        )
    )

    days = tuple(
        grid_start
        + timedelta(days=offset)
        for offset in range(
            (
                grid_end
                - grid_start
            ).days
            + 1
        )
    )

    week_count = (
        len(days)
        // 7
    )
    past_day_count = max(
        0,
        min(
            len(days),
            (
                reference_day
                - grid_start
            ).days,
        ),
    )

    past_day_selectors = ",\n".join(
        (
            ".sortable-component "
            f"> .sortable-container:nth-child({index})"
        )
        for index in range(
            1,
            past_day_count + 1,
        )
    )

    if past_day_selectors:

        past_day_style = (
            f"{past_day_selectors} {{"
            "opacity: 0.5 !important;"
            "pointer-events: none !important;"
            "cursor: not-allowed !important;"
            "}"
        )

    else:

        past_day_style = ""

    token_to_workout = {
        _plan_builder_workout_token(
            workout,
            index=index,
        ): workout
        for index, workout
        in enumerate(workouts)
    }

    original_day_by_token = {
        token: workout.day
        for token, workout
        in token_to_workout.items()
    }

    day_by_header = {
        day.strftime(
            "%a %d %b"
        ): day
        for day in days
    }

    containers = []

    for day in days:

        day_tokens = [
            token
            for token, workout
            in token_to_workout.items()
            if workout.day == day
        ]

        containers.append(
            {
                "header": day.strftime(
                    "%a %d %b"
                ),
                "items": day_tokens,
            }
        )

    custom_style = """
    .sortable-component {
        display: grid !important;
        grid-auto-flow: column !important;
        grid-template-rows:
            repeat(7, 40px) !important;
        grid-template-columns:
            repeat(
                __WEEK_COUNT__,
                minmax(0, 1fr)
            ) !important;
        gap: 4px !important;
        align-items: stretch !important;
        justify-content: stretch !important;
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        background: transparent !important;
        box-sizing: border-box !important;
    }

    .sortable-container {
        display: grid !important;
        grid-template-columns:
            3.8rem minmax(0, 1fr) !important;
        gap: 3px !important;
        align-items: center !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 40px !important;
        min-height: 40px !important;
        margin: 0 !important;
        padding: 3px !important;
        overflow: hidden !important;
        border:
            1px solid color-mix(
                in srgb,
                var(--text-color) 24%,
                transparent
            ) !important;
        border-radius: 5px !important;
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 88%,
                var(--background-color)
            ) !important;
        box-sizing: border-box !important;
    }

    .sortable-container-header {
        width: 100% !important;
        min-width: 0 !important;
        margin: 0 !important;
        padding: 0 2px !important;
        overflow: hidden !important;
        color:
            color-mix(
                in srgb,
                var(--text-color) 78%,
                transparent
            ) !important;
        background: transparent !important;
        font-size: 9px !important;
        font-weight: 650 !important;
        line-height: 1.1 !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        box-sizing: border-box !important;
    }

    .sortable-container-body {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 32px !important;
        min-height: 32px !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        background: transparent !important;
        box-sizing: border-box !important;
    }

    .sortable-item {
        display: block !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 28px !important;
        margin: 0 !important;
        padding: 6px 5px !important;
        overflow: hidden !important;
        border:
            1px solid color-mix(
                in srgb,
                var(--text-color) 30%,
                transparent
            ) !important;
        border-radius: 4px !important;
        color:
            var(--text-color) !important;
        background:
            var(--secondary-background-color) !important;
        font-size: 9px !important;
        font-weight: 650 !important;
        line-height: 1.1 !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        cursor: grab !important;
        box-sizing: border-box !important;
    }

    .sortable-item:hover {
        border-color:
            color-mix(
                in srgb,
                var(--text-color) 55%,
                transparent
            ) !important;
        background:
            color-mix(
                in srgb,
                var(--secondary-background-color) 82%,
                var(--text-color) 18%
            ) !important;
    }

    .sortable-item:active {
        cursor: grabbing !important;
    }

    .sortable-item.sortable-ghost {
        opacity: 0.35 !important;
    }

    __PAST_DAY_STYLE__
    """.replace(
        "__WEEK_COUNT__",
        str(week_count),
    ).replace(
        "__PAST_DAY_STYLE__",
        past_day_style,
    )

    result = sort_items(
        containers,
        multi_containers=True,
        custom_style=custom_style,
    )

    if not result:
        return draft

    resulting_day_by_token = {}

    for container in result:

        target_day = (
            day_by_header.get(
                container.get(
                    "header",
                    "",
                )
            )
        )

        if target_day is None:
            continue

        for token in container.get(
            "items",
            [],
        ):
            resulting_day_by_token[
                token
            ] = target_day

    moved_tokens = tuple(
        token
        for token, original_day
        in original_day_by_token.items()
        if (
            resulting_day_by_token.get(
                token,
                original_day,
            )
            != original_day
        )
    )

    if not moved_tokens:
        return draft

    moved_token = moved_tokens[0]

    source_day = (
        original_day_by_token[
            moved_token
        ]
    )

    target_day = (
        resulting_day_by_token[
            moved_token
        ]
    )

    if (
        source_day < reference_day
        or target_day < reference_day
    ):

        st.toast(
            (
                "Completed or past plan days "
                "cannot be changed."
            ),
            icon="⚠️",
            duration=3000,
        )

        return draft

    moved_workout = token_to_workout[moved_token]
    target_workout = next(
        (
            workout
            for workout in workouts
            if workout.day == target_day
        ),
        None,
    )

    if (
        _plan_builder_is_race(moved_workout)
        or (
            target_workout is not None
            and _plan_builder_is_race(target_workout)
        )
    ):
        st.toast(
            "Race dates must be changed in Events.",
            icon="⚠️",
            duration=3000,
        )
        return draft

    try:

        revised_draft = (
            draft.move_workout(
                source_day=source_day,
                target_day=target_day,
            )
        )

    except (
        LookupError,
        ValueError,
        TypeError,
    ) as error:

        st.toast(
            str(error),
            icon="⚠️",
            duration=3000,
        )

        return draft

    st.session_state[
        draft_key
    ] = revised_draft

    return revised_draft


def _plan_builder_is_race(workout) -> bool:
    """Returns whether a planned item represents an event."""

    return (
        str(workout.intensity or "").strip().lower()
        == "race effort"
        or "race" in str(workout.title or "").strip().lower()
    )


def _optional_float(value):
    return float(value) if value not in (None, "") else None


def _optional_int(value):
    return int(value) if value not in (None, "") else None


def _plan_builder_prescription(values, fallback=""):
    prescription = str(values.get("prescription") or fallback or "").strip()
    target = str(values.get("target_value") or "").strip()
    method = str(values.get("target_method") or "Target").strip()
    if target:
        target_line = f"{method}: {target}"
        if target_line.lower() not in prescription.lower():
            prescription = " · ".join(part for part in (prescription, target_line) if part)
    return prescription or None


def _show_plan_builder_interactive_board(
    *, draft, draft_key: str, plan_start: date,
    plan_end: date, reference_day: date, history=None,
):
    """Renders the clickable and draggable Plan Builder board."""
    grid_start = plan_start - timedelta(days=plan_start.weekday())
    grid_end = plan_end + timedelta(days=6 - plan_end.weekday())
    days = tuple(
        grid_start + timedelta(days=offset)
        for offset in range((grid_end - grid_start).days + 1)
    )
    workouts = tuple(sorted(draft.workouts, key=lambda item: item.scheduled_at))
    templates = {}
    for workout in draft.baseline_workouts:
        if workout.title and not _plan_builder_is_race(workout):
            template_title = "Trail Run" if workout.title == "Hill Run" else workout.title
            templates.setdefault(template_title, replace(workout, title=template_title))

    completed_workouts = []
    if history is not None:
        for completed in history:
            completed_day = completed.date
            if hasattr(completed_day, "date"):
                completed_day = completed_day.date()
            if completed_day is None or completed_day >= reference_day:
                continue
            completed_workouts.append({
                "id": f"completed-{completed.workout_id}",
                "day": completed_day.isoformat(),
                "title": completed.info.title or completed.sport or "Completed activity",
                "completed": True,
                "race": False,
            })

    def payload(workout):
        return {
            "id": workout.planned_workout_id,
            "day": workout.day.isoformat(),
            "title": workout.title or "Planned workout",
            "duration": round(workout.duration.total_seconds() / 60) if workout.duration else None,
            "distance": workout.distance,
            "elevation": workout.elevation_gain,
            "intensity": workout.intensity or "",
            "prescription": workout.prescription_summary or "",
            "objective": workout.objective or "",
            "structure": "\n".join(workout.structure),
            "race": _plan_builder_is_race(workout),
            "load": planned_workout_load(workout),
        }

    action = _plan_builder_board_component(
        days=[{"day": day.isoformat(), "label": day.strftime("%a %d %b"), "past": day < reference_day} for day in days],
        workouts=[
            *completed_workouts,
            *[payload(workout) for workout in workouts if workout.day >= reference_day],
        ],
        templates=[payload(workout) for workout in templates.values()],
        key="plan-builder-interactive-board",
        default=None,
    )
    if not action:
        return draft
    nonce = action.get("nonce")
    handled_key = "plan-builder-board-handled-action"
    if not nonce or st.session_state.get(handled_key) == nonce:
        return draft
    st.session_state[handled_key] = nonce
    kind = action.get("action")
    workout_id = action.get("workout_id")
    workout = next((item for item in workouts if item.planned_workout_id == workout_id), None)
    try:
        if kind == "move":
            target_day = date.fromisoformat(action["target_day"])
            if workout is None or workout.day < reference_day or target_day < reference_day:
                raise ValueError("Completed or past plan days cannot be changed.")
            if _plan_builder_is_race(workout):
                raise ValueError("Race dates must be changed in Events.")
            draft = draft.move_workout_id(workout_id=workout_id, target_day=target_day)
        elif kind == "delete":
            if workout is None or workout.day < reference_day:
                raise ValueError("Completed or past plan days cannot be changed.")
            if _plan_builder_is_race(workout):
                raise ValueError("Races must be removed in Events.")
            draft = draft.delete_workout(workout_id=workout_id)
        elif kind == "add":
            target_day = date.fromisoformat(action["target_day"])
            template = templates.get(action.get("template"))
            if target_day < reference_day:
                raise ValueError("Completed or past plan days cannot be changed.")
            if template is None:
                raise LookupError("The selected session template is unavailable.")
            values = action.get("values", {})
            configured_template = replace(
                template,
                title=str(values.get("title") or template.title or ""),
                duration=(
                    timedelta(minutes=_optional_int(values.get("duration")))
                    if _optional_int(values.get("duration")) is not None
                    else None
                ),
                distance=_optional_float(values.get("distance")),
                elevation_gain=_optional_float(values.get("elevation")),
                intensity=str(values.get("intensity") or "") or None,
                prescription_summary=_plan_builder_prescription(
                    values,
                    template.prescription_summary,
                ),
                objective=str(values.get("objective") or "") or None,
                structure=tuple(line.strip() for line in str(values.get("structure") or "").splitlines() if line.strip()),
            )
            draft = draft.add_workout(template=configured_template, workout_day=target_day, allow_occupied=True)
        elif kind == "edit":
            if workout is None or workout.day < reference_day:
                raise ValueError("Completed or past plan days cannot be changed.")
            if _plan_builder_is_race(workout):
                raise ValueError("Races must be edited in Events.")
            values = action.get("values", {})
            draft = draft.update_workout(
                workout_id=workout_id,
                title=str(values.get("title") or workout.title or ""),
                duration_minutes=_optional_int(values.get("duration")),
                distance=_optional_float(values.get("distance")),
                elevation_gain=_optional_float(values.get("elevation")),
                intensity=str(values.get("intensity") or ""),
                prescription_summary=_plan_builder_prescription(
                    values,
                    workout.prescription_summary,
                ),
                objective=str(values.get("objective") or ""),
                structure=tuple(line.strip() for line in str(values.get("structure") or "").splitlines() if line.strip()),
            )
    except (KeyError, LookupError, TypeError, ValueError) as error:
        st.toast(str(error), icon="⚠️", duration=3000)
        return draft
    st.session_state[draft_key] = draft
    return draft


def _show_plan_builder_session_actions(
    *,
    draft,
    draft_key: str,
    reference_day: date,
    plan_end: date,
):
    """Adds or removes non-race sessions in the isolated draft."""

    future_sessions = tuple(
        workout
        for workout in draft.workouts
        if (
            workout.day >= reference_day
            and not _plan_builder_is_race(workout)
        )
    )

    templates_by_title = {
        workout.title: workout
        for workout in draft.baseline_workouts
        if (
            workout.title
            and not _plan_builder_is_race(workout)
        )
    }

    add_column, remove_column = st.columns(2, gap="small")

    with add_column:
        with st.popover(
            "Add session",
            use_container_width=True,
        ):
            if not templates_by_title:
                st.caption("No reusable session templates are available.")
            else:
                template_title = st.selectbox(
                    "Session type",
                    tuple(sorted(templates_by_title)),
                    key="plan-builder-add-template",
                )
                target_day = st.date_input(
                    "Target day",
                    value=reference_day,
                    min_value=reference_day,
                    max_value=plan_end,
                    key="plan-builder-add-day",
                )
                if st.button(
                    "Add to draft",
                    key="plan-builder-add-confirm",
                    use_container_width=True,
                ):
                    try:
                        draft = draft.add_workout(
                            template=templates_by_title[template_title],
                            workout_day=target_day,
                        )
                    except (LookupError, TypeError, ValueError) as error:
                        st.toast(str(error), icon="⚠️", duration=3000)
                    else:
                        st.session_state[draft_key] = draft

    with remove_column:
        with st.popover(
            "Remove session",
            use_container_width=True,
        ):
            sessions_by_label = {
                f"{workout.day:%d %b} · {workout.title}": workout
                for workout in future_sessions
            }
            selected_label = (
                st.selectbox(
                    "Session",
                    tuple(sessions_by_label),
                    key="plan-builder-remove-session",
                )
                if sessions_by_label
                else None
            )
            if not sessions_by_label:
                st.caption("No future training session can be removed.")
            if st.button(
                "Remove from draft",
                key="plan-builder-remove-confirm",
                use_container_width=True,
                disabled=not sessions_by_label,
            ):
                selected = sessions_by_label[selected_label]
                draft = draft.delete_workout(
                    workout_day=selected.day,
                )
                st.session_state[draft_key] = draft

    return draft


def _plan_builder_recommendation(
    draft,
    *,
    reference_day: date,
) -> str | None:
    """Warns when draft edits compress demanding recovery."""

    demanding_tokens = (
        "tempo",
        "threshold",
        "lt2",
        "hill",
        "interval",
        "race",
    )
    demanding = tuple(
        sorted(
            (
                workout
                for workout in draft.workouts
                if (
                    workout.day >= reference_day
                    and any(
                        token in " ".join(
                            (
                                str(workout.title or ""),
                                str(workout.intensity or ""),
                                str(workout.focus or ""),
                            )
                        ).lower()
                        for token in demanding_tokens
                    )
                )
            ),
            key=lambda workout: workout.scheduled_at,
        )
    )
    for previous, following in zip(demanding, demanding[1:]):
        if (following.day - previous.day).days < 2:
            return (
                f"{previous.title} on {previous.day:%d %b} and "
                f"{following.title} on {following.day:%d %b} leave "
                "less than 48 hours of recovery. Consider moving one "
                "session or reducing the later session."
            )
    return None

@st.dialog(
    "Plan Builder",
    width="large",
)
def _show_plan_generation_confirmation(
    athlete,
    on_generate_plan,
    on_restore_revision=None,
) -> None:
    """
    Confirms the factual plan horizon before replacing the
    current persistent training plan.
    """

    notice = (
        PlanGenerationNoticePresenter(
            athlete
        ).build(
            reference_day=date.today()
        )
    )

    active_plan = (
        athlete.training_plan
    )

    draft_key = (
        "plan_builder_draft:"
        f"{active_plan.plan_id}:"
        f"{active_plan.active_revision_id or 'current'}"
    )

    if draft_key not in st.session_state:

        st.session_state[
            draft_key
        ] = (
            PlanBuilderDraft.from_plan(
                active_plan
            )
        )

    builder_draft = (
        st.session_state[
            draft_key
        ]
    )

    draft_plan = replace(
        active_plan,
        workouts=list(
            builder_draft.workouts
        ),
    )

    builder_plan = PlanPresenter(
        plan=draft_plan,
        history=athlete.history,
    ).build(
        reference_day=date.today()
    )

    st.markdown(
        """
        <style>
div[data-testid="stDialog"] [role="dialog"],
div[role="dialog"] {
    width: 94vw !important;
    min-width: 94vw !important;
    max-width: 1500px !important;
}
div[data-testid="stDialog"] [role="dialog"] {
    height: auto !important;
    max-height: 90vh !important;
    overflow: hidden !important;
}

div[data-testid="stDialog"]
[role="dialog"]
> div {
    min-height: 0 !important;
    max-height: 100% !important;
    overflow: hidden !important;
}

div[data-testid="stDialog"]
[role="dialog"]
[data-testid="stVerticalBlock"] {
    min-height: 0;
}

div[data-testid="stDialog"]
[role="dialog"]
[data-testid="stAltairChart"] {
    margin-bottom: 0.15rem;
}

div[data-testid="stDialog"] [role="dialog"] > div,
div[role="dialog"] > div {
    width: 100% !important;
    max-width: none !important;
    box-sizing: border-box;
}

div[role="dialog"] [data-testid="stVerticalBlock"] {
    width: 100% !important;
    max-width: none !important;
}

div[role="dialog"] [data-testid="stHorizontalBlock"] {
    width: 100% !important;
}

div[role="dialog"] .plan-builder-weeks {
    max-width: 100%;
    overflow-x: auto;
    overflow-y: hidden;
    scrollbar-width: thin;
}

div[role="dialog"] .plan-builder-library {
    max-width: 100%;
    overflow: hidden;
}

div[role="dialog"] .stSelectbox label,
div[role="dialog"] .stDateInput label {
    font-size: 0.68rem;
}

div[role="dialog"] [data-testid="stAlert"] {
    padding: 0.45rem 0.65rem;
    font-size: 0.68rem;
}
        .plan-builder-workspace {
            margin: 0.45rem 0 0.25rem;
            color: var(--text-color);
        }
        .plan-builder-workspace h4 { margin: .5rem 0 .25rem; font-size: .72rem; }
        .plan-builder-weeks { display: flex; gap: .5rem; overflow-x: auto; padding-bottom: .35rem; }
        .plan-builder-weeks article { flex: 0 0 10rem; max-height: 7rem; overflow: hidden; padding: .4rem; border: 1px solid rgba(0,0,0,.16); border-radius: .45rem; }
        .plan-builder-weeks header { margin-bottom: .3rem; font-size: .64rem; font-weight: 700; }
        .plan-builder-weeks article div { display: grid; grid-template-columns: 3.2rem 1fr; gap: .3rem; padding: .2rem 0; border-top: 1px solid rgba(0,0,0,.08); font-size: .58rem; }
        .plan-builder-library { display: flex; flex-wrap: wrap; gap: .4rem; }
        .plan-builder-library span { padding: .35rem .55rem; border: 1px solid rgba(0,0,0,.2); border-radius: .4rem; font-size: .62rem; font-weight: 650; }
        .plan-builder-empty { font-size: .7rem; opacity: .65; }
        .plan-generation-notice {
            color: var(--text-color);
            font-size: 0.84rem;
            line-height: 1.25;
        }

        .plan-generation-intro {
            margin: 0 0 0.4rem 0;
            color: var(--text-color);
        }

        .plan-generation-section-title {
            margin: 0 0 0.42rem 0;
            color: var(--text-color);
            font-size: 0.78rem;
            font-weight: 700;
        }

        .plan-generation-facts {
            border-top:
                1px solid color-mix(
                    in srgb,
                    var(--text-color) 22%,
                    transparent
                );
            border-bottom:
                1px solid color-mix(
                    in srgb,
                    var(--text-color) 22%,
                    transparent
                );
        }

        .plan-generation-row {
            display: grid;
            grid-template-columns:
                minmax(7rem, 0.8fr)
                minmax(0, 1.4fr);
            gap: 1rem;
            align-items: baseline;
            padding: 0.22rem 0;
            border-bottom:
                1px solid color-mix(
                    in srgb,
                    var(--text-color) 12%,
                    transparent
                );
        }

        .plan-generation-row:last-child {
            border-bottom: 0;
        }

        .plan-generation-label {
            color: var(--text-color);
            font-size: 0.7rem;
        }

        .plan-generation-value {
            color: var(--text-color);
            font-size: 0.76rem;
            font-weight: 650;
            text-align: right;
        }

        .plan-generation-later {
            margin-top: 0.4rem;
        }

        .plan-generation-copy {
            margin: 0;
            color: var(--text-color);
            font-size: 0.76rem;
            line-height: 1.42;
        }

        .plan-generation-note {
            margin: 0.5rem 0 0 0;
            color: var(--text-color);
            font-size: 0.68rem;
            line-height: 1.35;
        }

        .st-key-cancel-plan-generation button,
        .st-key-confirm-plan-generation button {
            min-height: 2.4rem;
            color: var(--text-color) !important;
            background: transparent !important;
            border-color:
                #9aa0aa !important;
            box-shadow: none !important;
        }

        .st-key-cancel-plan-generation button:hover,
        .st-key-confirm-plan-generation button:hover {
            color: var(--text-color) !important;
            background:
                rgba(0, 0, 0, 0.035) !important;
            border-color:
                #747b86 !important;
        }

        .st-key-confirm-plan-generation button {
            font-weight: 700;
        }

        div[data-testid="stDialog"]
        [role="dialog"]
        [data-testid="stVerticalBlock"] {
            gap: 0.35rem !important;
        }

        div[data-testid="stDialog"]
        [role="dialog"]
        h4 {
            margin-top: 0.15rem !important;
            margin-bottom: 0.15rem !important;
        }

        div[data-testid="stDialog"]
        [role="dialog"]
        [data-testid="stCaptionContainer"] {
            margin: 0 !important;
        }

        div[data-testid="stDialog"]
        [role="dialog"]
        [data-testid="stAltairChart"] {
            height: 125px !important;
            min-height: 125px !important;
            margin: 0 !important;
        }

        div[data-testid="stDialog"]
        [role="dialog"]
        [data-testid="stButton"] {
            margin-top: 0 !important;
        }

        .st-key-plan-builder-reset-drag button,
        .st-key-cancel-plan-generation button,
        .st-key-confirm-plan-generation button {
            color: var(--text-color) !important;
            border-color:
                #9aa0aa !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    components.html(
        """
        <script>
        const resizePlanBuilder = () => {
            const documentRoot = (
                window.parent.document
            );

            const dialogs = Array.from(
                documentRoot.querySelectorAll(
                    '[role="dialog"]'
                )
            );

            const dialog = dialogs.at(-1);

            if (!dialog) {
                return;
            }

            documentRoot.documentElement.style.setProperty(
                'overflow',
                'hidden',
                'important'
            );
            documentRoot.body.style.setProperty(
                'overflow',
                'hidden',
                'important'
            );

            const dialogParent = (
                dialog.parentElement
            );

            const dialogContent = (
                dialog.querySelector(
                    '[data-testid="stVerticalBlock"]'
                )
            );

            const targets = [
                dialogParent,
                dialog,
            ].filter(Boolean);

            targets.forEach((target) => {
                target.style.setProperty(
                    'width',
                    '94vw',
                    'important'
                );

                target.style.setProperty(
                    'min-width',
                    '94vw',
                    'important'
                );

                target.style.setProperty(
                    'max-width',
                    '1500px',
                    'important'
                );
            });

            dialog.style.setProperty(
                'overflow-x',
                'hidden',
                'important'
            );

            if (dialogContent) {
                dialogContent.style.setProperty(
                    'width',
                    '100%',
                    'important'
                );

                dialogContent.style.setProperty(
                    'max-width',
                    'none',
                    'important'
                );
            }
        };

        resizePlanBuilder();

        const unlockPlanBuilderPage = () => {
            const documentRoot = window.parent.document;
            documentRoot.documentElement.style.removeProperty('overflow');
            documentRoot.body.style.removeProperty('overflow');
        };

        window.addEventListener('pagehide', unlockPlanBuilderPage);
        window.addEventListener('beforeunload', unlockPlanBuilderPage);

        let resizeAttempts = 0;

        const resizeInterval = window.setInterval(
            () => {
                resizePlanBuilder();
                resizeAttempts += 1;

                if (resizeAttempts >= 40) {
                    window.clearInterval(
                        resizeInterval
                    );
                }
            },
            50
        );

        const observer = new MutationObserver(
            resizePlanBuilder
        );

        observer.observe(
            window.parent.document.body,
            {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: [
                    'style',
                    'class',
                ],
            }
        );

        window.setTimeout(
            () => observer.disconnect(),
            4000
        );
        </script>
        """,
        height=0,
        width=0,
    )

    revisions = tuple(
        reversed(
            tuple(
                revision
                for revision in athlete.training_plan.revisions
                if revision.revision_id
                != athlete.training_plan.active_revision_id
            )
        )
    )

    build_tab, recovery_tab = st.tabs(
        ["Build plan", "Plan recovery"]
    )

    with build_tab:

        with st.expander(
            "Plan horizon",
            expanded=False,
        ):
            st.html(
                _plan_generation_notice_html(
                    notice
                )
            )

        st.markdown(
            "#### Complete plan timeline"
        )

        timeline_slot = st.empty()

        st.markdown(
            "#### Plan structure by week"
        )

        st.caption(
            "Each column represents one week. "
            "Drag a session to an empty day to move it, "
            "or onto another session to exchange their days."
        )

        builder_draft = (
            _show_plan_builder_interactive_board(
                draft=builder_draft,
                draft_key=draft_key,
                plan_start=(
                    active_plan.start_date
                ),
                plan_end=(
                    active_plan.end_date
                ),
                reference_day=date.today(),
                history=athlete.history,
            )
        )

        draft_recommendation = (
            _plan_builder_recommendation(
                builder_draft,
                reference_day=date.today(),
            )
        )

        if draft_recommendation:
            st.warning(draft_recommendation)

        saved_plan = PlanPresenter(
            plan=active_plan,
            history=athlete.history,
        ).build(
            reference_day=date.today()
        )

        draft_plan = replace(
            active_plan,
            workouts=list(
                builder_draft.workouts
            ),
        )

        builder_plan = PlanPresenter(
            plan=draft_plan,
            history=athlete.history,
        ).build(
            reference_day=date.today()
        )

        builder_chart_plan = replace(
            builder_plan,
            original_chart_points=tuple(
                saved_plan.chart_points
            ),
        )

        chart_revision = abs(
            hash(
                tuple(
                    (
                        index,
                        workout.scheduled_at.isoformat(),
                        workout.title,
                        (
                            workout.duration.total_seconds()
                            if workout.duration is not None
                            else None
                        ),
                        workout.distance,
                        workout.elevation_gain,
                    )
                    for index, workout
                    in enumerate(
                        builder_draft.workouts
                    )
                )
            )
        )

        timeline_slot.altair_chart(
            _planned_load_chart(
                builder_chart_plan
            ),
            use_container_width=True,
            key=(
                "plan-builder-timeline-"
                f"{chart_revision}"
            ),
        )


        (
            reset_column,
            cancel_column,
            generate_column,
        ) = st.columns(
            [1, 1, 1],
            gap="small",
        )

        with reset_column:

            if st.button(
                "Reset changes",
                key="plan-builder-reset-drag",
                use_container_width=True,
                disabled=(
                    not builder_draft.has_changes
                ),
            ):

                st.session_state[
                    draft_key
                ] = (
                    builder_draft.reset()
                )

        with cancel_column:

            if st.button(
                "Cancel",
                key="cancel-plan-generation",
                use_container_width=True,
            ):

                return

        with generate_column:

            if st.button(
                "Generate plan",
                key="confirm-plan-generation",
                use_container_width=True,
            ):

                on_generate_plan(
                    athlete
                )

    with recovery_tab:
        st.caption(
            "Restore an earlier plan version without "
            "deleting the current revision."
        )

        if not revisions:
            st.info("No earlier plan revisions are available.")

        for revision in revisions:
            label = (
                f"{revision.created_on:%d %b %Y} · "
                f"{revision.source.replace('_', ' ').title()}"
            )
            left, right = st.columns([4, 1], gap="small")
            with left:
                st.caption(label)
            with right:
                if st.button(
                    "Restore",
                    key=f"restore-plan-{revision.revision_id}",
                    use_container_width=True,
                    disabled=(on_restore_revision is None),
                ):
                    on_restore_revision(revision.revision_id)
                    st.rerun()

def _show_plan_actions(
    plan,
    athlete,
    on_generate_plan,
    on_restore_revision=None,
) -> None:
    """Render plan generation in the plan's right column."""
    generate_plan_requested = (
        st.button(
            "Generate plan",
            icon=(
                ":material/auto_awesome:"
            ),
            type="primary",
            use_container_width=True,
            key="plan_generate",
            disabled=(
                on_generate_plan is None
            ),
        )
    )

    if generate_plan_requested:

        if on_restore_revision is None:

            _show_plan_generation_confirmation(
                athlete,
                on_generate_plan,
            )

        else:

            _show_plan_generation_confirmation(
                athlete,
                on_generate_plan,
                on_restore_revision,
            )


def _show_plan_weeks(plan, *, reference_day: date) -> None:
    """Keep chronological weeks and initially reveal the current one."""

    weeks = tuple(plan.weeks)
    current_index = next(
        (
            index
            for index, week in enumerate(weeks)
            if week.start_date <= reference_day <= week.end_date
        ),
        None,
    )

    def show_week(week) -> None:
        if (
            current_index is not None
            and week is weeks[current_index]
        ):
            st.markdown(
                '<span class="plan-current-week-anchor"></span>',
                unsafe_allow_html=True,
            )
        with st.expander(
            _week_summary_label(week, reference_day=reference_day),
            expanded=False,
        ):
            st.markdown(_week_html(week), unsafe_allow_html=True)

    with st.container(height=220, border=True, key="plan_weeks_scroll"):
        for week in weeks:
            show_week(week)

    if current_index not in (None, 0):
        components.html(
            """
            <script>
            const positionCurrentWeek = () => {
                const root = window.parent.document.querySelector(
                    ".st-key-plan_weeks_scroll"
                );
                const anchor = root?.querySelector(
                    ".plan-current-week-anchor"
                );
                if (!root || !anchor || root.dataset.currentWeekPositioned) return;
                root.dataset.currentWeekPositioned = "true";
                root.scrollTop += anchor.getBoundingClientRect().top
                    - root.getBoundingClientRect().top - 4;
            };
            requestAnimationFrame(() => requestAnimationFrame(positionCurrentWeek));
            </script>
            """,
            height=0,
            width=0,
        )


def show_plan_page(
    athlete,
    *,
    on_generate_plan=None,
    on_restore_revision=None,
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

    _compact_plan_layout_styles(
        _plan_header_caption(plan)
    )

    with st.container(key="plan_page_columns"):
        main_column, sidebar_column = st.columns(
            [3.4, 1],
            gap="medium",
        )

    with sidebar_column:
        _show_plan_actions(
            plan,
            athlete,
            on_generate_plan,
            on_restore_revision,
        )

    if not plan.weeks:

        with main_column:
            st.info(
                "No training plan is available. "
                "Generate a plan to begin."
            )

        return

    summary = _plan_summary_metrics(plan)

    current_week = _current_plan_week(
        plan.weeks,
        reference_day=today,
    )

    upcoming_events = CalendarPresenter(
        history=athlete.history,
        training_plan=athlete.training_plan,
        events=athlete.events,
    ).upcoming_events(
        reference_day=today,
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

        summary_html = summary_cards_html(
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

        st.markdown(
            (
                "<style>"
                + phase_timeline_styles()
                + summary_cards_styles()
                + "</style>"
                + '<div class="plan-overview">'
                + (timeline_html or "")
                + summary_html
                + "</div>"
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
            _planned_load_chart(plan),
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
            _distance_elevation_chart(plan),
            use_container_width=True,
        )

        _plan_styles()

    with sidebar_column:

        sidebar_html = (
            '<div class="plan-sidebar-stack">'
            + _sidebar_phase_html(
                plan.current_phase
            )
            + _sidebar_week_html(
                current_week
            )
            + "</div>"
        )

        with st.container(
            key="plan_summary_cards",
        ):
            st.html(
                (
                    "<style>"
                    + _sidebar_styles()
                    + "</style>"
                    + sidebar_html
                )
            )

    with st.container(
        key="plan_lower_row",
    ):
        (
            weeks_column,
            adaptation_column,
            events_column,
        ) = st.columns(
            [1.7, 1.7, 1],
            gap="medium",
            vertical_alignment="top",
        )

        with weeks_column:
            with st.container(
                key="plan_weeks_section",
            ):
                st.markdown(
                    (
                        '<div class="plan-weeks-heading">'
                        "Plan weeks"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                _show_plan_weeks(
                    plan,
                    reference_day=today,
                )

        with adaptation_column:
            with st.container(
                key="plan_latest_adaptation",
            ):
                st.markdown(
                    (
                        '<div class="plan-weeks-heading '
                        'plan-adaptation-heading">'
                        "<span>Plan adaptation</span>"
                        '<details class="plan-adaptation-help">'
                        '<summary aria-label="How plan adaptation works">'
                        "?"
                        "</summary>"
                        '<div class="plan-adaptation-help-panel" '
                        'role="note">'
                        "<strong>How adaptation works</strong>"
                        "<p>"
                        "PerformanceLab compares planned and completed "
                        "training by load, sport, session purpose and "
                        "physiological focus."
                        "</p>"
                        "<p>"
                        "A similar load does not automatically replace a "
                        "missing stimulus. For example, Tempo or LT2 work "
                        "does not fully replace Hill Reps when preparing "
                        "for a trail race."
                        "</p>"
                        "<p>"
                        "Before the race, the plan prioritises event "
                        "specificity, recovery between demanding sessions "
                        "and the athlete's current training state."
                        "</p>"
                        "<p>"
                        "Easy, long and quality sessions have different "
                        "roles. A Long Run is not removed automatically "
                        "to recover a missed LT2 session."
                        "</p>"
                        "<p>"
                        "Changes to session type will be presented as a "
                        "suggestion and require athlete confirmation. If "
                        "there is no safe opportunity, the missing stimulus "
                        "is not forced into taper or regeneration."
                        "</p>"
                        "</div>"
                        "</details>"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                st.html(
                    (
                        "<style>"
                        + _sidebar_styles()
                        + "</style>"
                        + _sidebar_adaptation_html(
                            plan.latest_adaptation,
                            reference_day=(
                                plan.reference_day
                            ),
                            show_heading=False,
                            stimulus_suggestion=(
                                plan
                                .latest_stimulus_suggestion
                            ),
                        )
                    )
                )

        with events_column:
            with st.container(
                key="plan_upcoming_events",
            ):
                st.markdown(
                    (
                        '<div class="plan-weeks-heading">'
                        "Upcoming events"
                        "</div>"
                    ),
                    unsafe_allow_html=True,
                )

                st.html(
                    (
                        "<style>"
                        + _sidebar_styles()
                        + upcoming_events_styles()
                        + "</style>"
                        + (
                            '<section class="plan-sidebar-card '
                            'plan-upcoming-events-card">'
                        )
                        + upcoming_events_html(upcoming_events)
                        + "</section>"
                    )
                )
