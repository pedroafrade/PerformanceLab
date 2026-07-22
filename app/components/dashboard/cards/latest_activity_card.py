"""
PerformanceLab

Latest activity dashboard card.
"""

from __future__ import annotations

from datetime import timedelta
from html import escape

import streamlit as st

from performancelab.presentation.dashboard_models import (
    LatestActivityCardData,
)


def _format_duration(
    duration: timedelta | None,
) -> str:
    """
    Format duration as H:MM:SS or MM:SS.
    """

    if duration is None:
        return "—"

    total_seconds = max(
        0,
        round(duration.total_seconds()),
    )

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes, seconds = divmod(
        remainder,
        60,
    )

    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    return f"{minutes}:{seconds:02d}"


def _format_pace(
    distance: float | None,
    duration: timedelta | None,
) -> str:
    """
    Format average pace in minutes per kilometre.
    """

    if (
        distance is None
        or distance <= 0
        or duration is None
    ):
        return "—"

    seconds_per_km = (
        duration.total_seconds()
        / distance
    )

    minutes, seconds = divmod(
        round(seconds_per_km),
        60,
    )

    return f"{minutes}:{seconds:02d}/km"


def _format_number(
    value: float | None,
    unit: str,
) -> str:
    """
    Format an optional numeric value.
    """

    if value is None:
        return "—"

    return f"{value:.0f} {unit}"


def _format_heart_rate(
    average: float | None,
    maximum: float | None,
) -> str:
    """
    Format average and maximum heart rate.
    """

    if average is None and maximum is None:
        return "—"

    average_text = (
        f"{average:.0f}"
        if average is not None
        else "—"
    )

    maximum_text = (
        f"{maximum:.0f}"
        if maximum is not None
        else "—"
    )

    return f"{average_text} / {maximum_text} bpm"


def _detail_row(
    label: str,
    value: str,
) -> str:
    """
    Build one aligned activity detail row.
    """

    return (
        "<div style='"
        "display:grid;"
        "grid-template-columns:minmax(0,1fr) auto;"
        "align-items:baseline;"
        "column-gap:0.75rem;"
        "margin-bottom:0.40rem;"
        "font-size:0.78rem;"
        "line-height:1.15;"
        "'>"
        "<span style='color:#8b949e;'>"
        f"{escape(label)}"
        "</span>"
        "<span style='"
        "font-weight:600;"
        "text-align:right;"
        "white-space:nowrap;"
        "'>"
        f"{escape(value)}"
        "</span>"
        "</div>"
    )


def latest_activity_card(
    data: LatestActivityCardData,
) -> None:
    """
    Render the latest activity card.
    """

    if data.workout_date is None:

        st.info(
            "No activities recorded."
        )

        return

    title = escape(
        data.title
        or data.sport
        or "Activity"
    )

    date_text = data.workout_date.strftime(
        "%d %b %Y"
    )

    distance = (
        f"{data.distance:.1f} km"
        if data.distance is not None
        else "—"
    )

    elevation = (
        f"D+{data.elevation_gain:.0f} m"
        if data.elevation_gain is not None
        else "D+—"
    )

    parts = [
        "<div style='",
        "display:flex;",
        "flex-direction:column;",
        "width:100%;",
        "padding-top:0.25rem;",
        "padding-bottom:0.20rem;",
        "box-sizing:border-box;",
        "'>",

        "<div style='",
        "display:flex;",
        "align-items:baseline;",
        "justify-content:space-between;",
        "gap:0.75rem;",
        "margin-bottom:0.60rem;",
        "'>",

        "<div style='",
        "min-width:0;",
        "overflow:hidden;",
        "font-size:0.86rem;",
        "font-weight:650;",
        "line-height:1.15;",
        "text-overflow:ellipsis;",
        "white-space:nowrap;",
        "'>",
        title,
        "</div>",

        "<div style='",
        "flex:0 0 auto;",
        "color:#8b949e;",
        "font-size:0.70rem;",
        "line-height:1.15;",
        "white-space:nowrap;",
        "'>",
        date_text,
        "</div>",

        "</div>",

        "<div style='",
        "display:flex;",
        "align-items:baseline;",
        "gap:0.40rem;",
        "margin-bottom:0.75rem;",
        "line-height:1;",
        "'>",

        "<span style='",
        "font-size:1.35rem;",
        "font-weight:700;",
        "'>",
        distance,
        "</span>",

        "<span style='",
        "color:#8b949e;",
        "font-size:0.75rem;",
        "font-weight:500;",
        "'>",
        "· ",
        elevation,
        "</span>",

        "</div>",

        _detail_row(
            "Duration",
            _format_duration(
                data.duration
            ),
        ),
        _detail_row(
            "Pace",
            _format_pace(
                data.distance,
                data.duration,
            ),
        ),
        _detail_row(
            "HR (avg/max)",
            _format_heart_rate(
                data.average_heart_rate,
                data.maximum_heart_rate,
            ),
        ),
        _detail_row(
            "Power",
            _format_number(
                data.average_power,
                "W",
            ),
        ),

        "</div>",
    ]

    st.markdown(
        "".join(parts),
        unsafe_allow_html=True,
    )