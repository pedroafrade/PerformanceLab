"""
PerformanceLab

Latest activity dashboard card.
"""

from __future__ import annotations

from datetime import timedelta
from html import escape
from textwrap import dedent

import streamlit.components.v1 as components

from performancelab.presentation.dashboard_models import (
    LatestActivityCardData,
)


_RUNNING_ICON_DATA_URI = (
    "data:image/png;base64,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"
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


def latest_activity_card(
    data: LatestActivityCardData,
) -> None:
    """
    Render the latest activity card.
    """

    if data.workout_date is None:
        components.html(
            """
            <div style="
                color: rgba(49, 51, 63, 0.64);
                font-family: sans-serif;
                font-size: 0.82rem;
            ">
                No activities recorded.
            </div>
            """,
            height=48,
        )
        return

    title = escape(
        data.title
        or data.sport
        or "Activity"
    )

    distance = (
        f"{data.distance:.2f} km"
        if data.distance is not None
        else "—"
    )

    elevation = _format_number(
        data.elevation_gain,
        "m",
    )

    date_text = data.workout_date.strftime(
        "%d/%m/%Y"
    )

    html = dedent(
        f"""
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * {{
                    box-sizing: border-box;
                }}

                html,
                body {{
                    margin: 0;
                    padding: 0;
                    background: transparent;
                    color: #31333f;
                    font-family:
                        Inter,
                        -apple-system,
                        BlinkMacSystemFont,
                        "Segoe UI",
                        sans-serif;
                }}

                .latest-activity-card {{
                    display: flex;
                    align-items: flex-start;
                    gap: 0.9rem;
                    width: 100%;
                }}

                .latest-activity-logo {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    width: 3.9rem;
                    height: 3.9rem;
                    flex: 0 0 3.9rem;
                    margin-top: 1.45rem;
                }}

                .latest-activity-logo img {{
                    display: block;
                    width: 3.7rem;
                    height: 3.7rem;
                    object-fit: contain;
                }}

                .latest-activity-content {{
                    display: flex;
                    flex-direction: column;
                    align-items: flex-start;
                    min-width: 0;
                }}

                .latest-activity-date {{
                    margin-bottom: 0.25rem;
                    color: rgba(49, 51, 63, 0.58);
                    font-size: 0.72rem;
                    line-height: 1.2;
                }}

                .latest-activity-title {{
                    overflow: hidden;
                    width: 100%;
                    margin-bottom: 0.15rem;
                    color: rgba(49, 51, 63, 0.68);
                    font-size: 0.78rem;
                    line-height: 1.2;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }}

                .latest-activity-distance {{
                    margin-bottom: 0.45rem;
                    font-size: 1.45rem;
                    font-weight: 700;
                    line-height: 1.05;
                }}

                .latest-activity-distance small {{
                    margin-left: 0.35rem;
                    color: rgba(49, 51, 63, 0.68);
                    font-size: 0.76rem;
                    font-weight: 500;
                }}

                .latest-activity-row {{
                    display: flex;
                    align-items: baseline;
                    gap: 0.45rem;
                    margin-top: 0.22rem;
                    font-size: 0.77rem;
                    line-height: 1.3;
                }}

                .latest-activity-label {{
                    min-width: 4.8rem;
                    color: rgba(49, 51, 63, 0.58);
                }}

                .latest-activity-value {{
                    font-weight: 620;
                }}
            </style>
        </head>

        <body>
            <div class="latest-activity-card">
                <div class="latest-activity-logo">
                    <img
                        src="{_RUNNING_ICON_DATA_URI}"
                        alt=""
                    />
                </div>

                <div class="latest-activity-content">
                    <div class="latest-activity-date">
                        {date_text}
                    </div>

                    <div class="latest-activity-title">
                        {title}
                    </div>

                    <div class="latest-activity-distance">
                        {distance}
                        <small>D+ {elevation}</small>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Duration
                        </span>
                        <span class="latest-activity-value">
                            {_format_duration(data.duration)}
                        </span>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Pace
                        </span>
                        <span class="latest-activity-value">
                            {_format_pace(data.distance, data.duration)}
                        </span>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Avg HR
                        </span>
                        <span class="latest-activity-value">
                            {_format_number(
                                data.average_heart_rate,
                                "bpm",
                            )}
                        </span>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Max HR
                        </span>
                        <span class="latest-activity-value">
                            {_format_number(
                                data.maximum_heart_rate,
                                "bpm",
                            )}
                        </span>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Power
                        </span>
                        <span class="latest-activity-value">
                            {_format_number(
                                data.average_power,
                                "W",
                            )}
                        </span>
                    </div>

                    <div class="latest-activity-row">
                        <span class="latest-activity-label">
                            Active kcal
                        </span>
                        <span class="latest-activity-value">
                            {_format_number(
                                data.active_calories,
                                "kcal",
                            )}
                        </span>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    ).strip()

    components.html(
        html,
        height=225,
        scrolling=False,
    )