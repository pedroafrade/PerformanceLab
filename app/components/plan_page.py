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

    return [
        {
            "Date": point.day.isoformat(),
            "Planned load": (
                point.planned_load
            ),
            "Session": point.title,
            "Phase": (
                point.phase
                or "Unassigned"
            ),
            "Session type": (
                "Race"
                if point.is_race
                else "Training"
            ),
        }
        for point in chart_points
        if point.planned_load is not None
    ]


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
    """

    if (
        plan.start_date is None
        or plan.end_date is None
    ):
        return alt.Scale()

    return alt.Scale(
        domain=[
            plan.start_date.isoformat(),
            plan.end_date.isoformat(),
        ]
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
                    "Phase:N",
                    title="Phase",
                ),
                alt.Tooltip(
                    "Planned load:Q",
                    title="Session load",
                    format=".0f",
                ),
            ],
        )
    )

    training_line = (
        training_base
        .mark_line(
            interpolate="monotone",
            strokeWidth=1.8,
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
                    "Phase:N",
                    title="Phase",
                ),
                alt.Tooltip(
                    "Planned load:Q",
                    title="Race load",
                    format=".0f",
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
            race_rules,
            race_points,
        )
    )

    return (
        alt.layer(
            session_load_chart,
            weekly_load_line,
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
            "Distance:Q",
            title="Distance",
            format=".1f",
        ),
        alt.Tooltip(
            "Elevation:Q",
            title="Elevation",
            format=".0f",
        ),
        alt.Tooltip(
            "Point type:N",
            title="Point",
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

    return (
        alt.layer(
            distance_line,
            weekly_distance_points,
            race_distance_points,
            elevation_line,
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

def _week_html(
    week,
) -> str:
    """
    Renders the workouts of one plan week.
    """

    parts = [
        '<div class="complete-plan-week">'
    ]

    for workout in week.workouts:

        status = (
            str(
                workout.status
                or "pending"
            )
            .replace("_", "-")
        )

        title = escape(
            workout.title
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

        prescription = (
            escape(
                workout.prescription_summary
            )
            if workout.prescription_summary
            else ""
        )

        parts.append(
            (
                '<div class="complete-plan-session '
                f'status-{escape(status)}">'
                '<div class="complete-plan-session-date">'
                f"{workout.scheduled_at.strftime('%a %d')}"
                "</div>"
                '<div class="complete-plan-session-main">'
                f"<strong>{title}</strong>"
                f"<span>{sport}</span>"
            )
        )

        if prescription:

            parts.append(
                (
                    '<span class="complete-plan-prescription">'
                    f"{prescription}"
                    "</span>"
                )
            )

        parts.append(
            (
                "</div>"
                '<div class="complete-plan-session-value">'
                f"{duration}"
                "</div>"
                '<div class="complete-plan-session-value">'
                f"{intensity}"
                "</div>"
                '<div class="complete-plan-session-status">'
                f"{escape(_status_label(workout.status))}"
                "</div>"
                "</div>"
            )
        )

    parts.append(
        "</div>"
    )

    return "".join(parts)

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

    weeks_label = (
        "week remaining"
        if weeks_remaining == 1
        else "weeks remaining"
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
        '<div class="plan-sidebar-remaining">'
        '<span class="plan-sidebar-remaining-value">'
        f"{weeks_remaining}"
        "</span>"
        '<span class="plan-sidebar-remaining-label">'
        f"{weeks_label}"
        "</span>"
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

.plan-sidebar-remaining {
    display: flex;
    align-items: baseline;
    gap: 0.45rem;
}

.plan-sidebar-remaining-value {
    font-size: 1.65rem;
    font-weight: 700;
    line-height: 1;
}

.plan-sidebar-remaining-label {
    font-size: 0.7rem;
    opacity: 0.62;
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

.plan-sidebar-empty {
    margin: 0;
    font-size: 0.78rem;
    opacity: 0.6;
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
            gap: 0.3rem;
            padding-top: 0.15rem;
        }

        .complete-plan-session {
            display: grid;
            grid-template-columns:
                minmax(64px, 0.65fr)
                minmax(220px, 3.2fr)
                minmax(72px, 0.7fr)
                minmax(95px, 0.9fr)
                minmax(78px, 0.75fr);
            gap: 0.55rem;
            align-items: center;
            padding: 0.5rem 0.65rem;
            border: 1px solid rgba(128, 128, 128, 0.22);
            border-left: 4px solid #4f86f7;
            border-radius: 0.5rem;
            background: var(--background-color);
        }

        .complete-plan-session.status-equivalent {
            border-left-color: #39a96b;
        }

        .complete-plan-session.status-modified,
        .complete-plan-session.status-substitute {
            border-left-color: #d28b27;
        }

        .complete-plan-session.status-missed {
            border-left-color: #e05a5a;
            opacity: 0.72;
        }

        .complete-plan-session-date {
            font-size: 0.76rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .complete-plan-session-main {
            min-width: 0;
            display: flex;
            flex-direction: column;
            gap: 0.12rem;
        }

        .complete-plan-session-main strong,
        .complete-plan-session-main span {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .complete-plan-session-main span,
        .complete-plan-session-value {
            color: rgba(128, 128, 128, 0.95);
            font-size: 0.76rem;
        }

        .complete-plan-prescription {
            color: inherit !important;
        }

        .complete-plan-session-status {
            font-size: 0.72rem;
            font-weight: 700;
            text-align: right;
        }

        @media (max-width: 900px) {
            .complete-plan-session {
                grid-template-columns:
                    minmax(60px, 0.7fr)
                    minmax(160px, 2fr)
                    minmax(80px, 0.8fr);
            }

            .complete-plan-session-value {
                display: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
def _compact_plan_layout_styles() -> None:
    """
    Balances compactness and readability on the plan page.
    """

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 2.4rem;
            padding-bottom: 1rem;
        }

        div[data-testid="stMainBlockContainer"] h1 {
            margin-top: 0;
            margin-bottom: 0.2rem;
            line-height: 1.2;
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

        div[data-testid="stExpander"] {
            margin-bottom: 0.15rem;
            border-radius: 0.55rem;
        }

        div[data-testid="stExpander"] details {
            border: 1px solid rgba(128, 128, 128, 0.24);
            border-radius: 0.55rem;
            overflow: hidden;
            background: rgba(128, 128, 128, 0.015);
        }

        div[data-testid="stExpander"] details summary {
            min-height: 2.15rem;
            padding-top: 0.35rem;
            padding-bottom: 0.35rem;
            font-size: 0.72rem;
            font-weight: 650;
        }

        div[data-testid="stExpander"] details summary:hover {
            background: rgba(128, 128, 128, 0.045);
        }

        div[data-testid="stExpander"] details[open] summary {
            border-bottom:
                1px solid rgba(128, 128, 128, 0.16);
            background: rgba(128, 128, 128, 0.035);
        }

        div[data-testid="stExpander"] details > div {
            padding-top: 0.2rem;
            padding-bottom: 0.25rem;
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
        """,
        unsafe_allow_html=True,
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

    _compact_plan_layout_styles()

    title_column, action_column = (
        st.columns(
            [4.5, 1.5],
            gap="medium",
        )
    )

    with title_column:

        st.title(
            "Plan"
        )

        st.caption(
            "Review the complete persistent plan "
            "through the target event and recovery."
        )

    with action_column:

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

    plan = PlanPresenter(
        plan=athlete.training_plan,
        history=athlete.history,
    ).build(
        reference_day=today
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
            + (
                '<section class="plan-sidebar-card">'
                '<div class="plan-sidebar-heading">'
                '<span class="plan-sidebar-icon">↻</span>'
                "<span>Latest adaptation</span>"
                "</div>"
                '<p class="plan-sidebar-empty">'
                "Coming soon"
                "</p>"
                "</section>"
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