"""
PerformanceLab

Weekly multisport summary dashboard card.
"""

from __future__ import annotations

from datetime import timedelta
from html import escape
from textwrap import dedent

import streamlit.components.v1 as components

from performancelab.presentation.dashboard_models import (
    WeeklySportSummaryData,
    WeeklySummaryCardData,
)


_SPORT_ICONS = {
    "Running": """
        <svg viewBox="0 0 24 24">
            <circle cx="15.5" cy="4.5" r="2"/>
            <path d="M9 9l4-3 3 3 4 1"/>
            <path d="M9 9l-3 4-4 1"/>
            <path d="M11 10l-1 5 4 3"/>
            <path d="M10 15l-4 4-2 3"/>
            <path d="M14 18l-1 4"/>
        </svg>
    """,
    "Cycling": """
        <svg viewBox="0 0 24 24">
            <circle cx="6" cy="17" r="4"/>
            <circle cx="18" cy="17" r="4"/>
            <path d="M8 17l4-8 4 8"/>
            <path d="M8 17h8"/>
            <path d="M10 9h4"/>
            <path d="M13 6h3"/>
        </svg>
    """,
    "Swimming": """
        <svg viewBox="0 0 24 24">
            <circle cx="15" cy="6" r="2"/>
            <path d="M4 12l4-3 4 3 4-3 4 3"/>
            <path d="M3 16c2 0 2 1 4 1s2-1 4-1 2 1 4 1 2-1 4-1"/>
            <path d="M3 20c2 0 2 1 4 1s2-1 4-1 2 1 4 1 2-1 4-1"/>
        </svg>
    """,
    "Other": """
        <svg viewBox="0 0 24 24">
            <path d="M3 9v6"/>
            <path d="M6 7v10"/>
            <path d="M18 7v10"/>
            <path d="M21 9v6"/>
            <path d="M6 12h12"/>
        </svg>
    """,
}


def _format_duration(
    duration: timedelta,
) -> str:
    """
    Format a duration compactly.
    """

    total_minutes = round(
        duration.total_seconds() / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:
        return f"{hours}h {minutes:02d}m"

    if hours:
        return f"{hours}h"

    return f"{minutes}m"


def _format_distance(
    sport: str,
    distance: float,
) -> str:
    """
    Format sport-specific distance.
    """

    if sport == "Swimming":
        return f"{distance * 1000:,.0f} m".replace(
            ",",
            " ",
        )

    return f"{distance:.1f} km"


def _metric_row(
    label: str,
    value: str,
) -> str:
    """
    Build one summary metric row.
    """

    return (
        '<div class="weekly-summary-row">'
        f'<span>{escape(label)}</span>'
        f'<strong>{escape(value)}</strong>'
        "</div>"
    )


def _sport_block(
    item: WeeklySportSummaryData,
) -> str:
    """
    Build one sport summary block.
    """

    rows = []

    if item.sport != "Other":
        rows.append(
            _metric_row(
                "Volume",
                _format_distance(
                    item.sport,
                    item.distance,
                ),
            )
        )

    rows.append(
        _metric_row(
            "Time",
            _format_duration(
                item.duration
            ),
        )
    )

    if (
        item.sport
        in ("Running", "Cycling")
    ):
        rows.append(
            _metric_row(
                "Elevation",
                f"{item.elevation_gain:.0f} m",
            )
        )

    rows.append(
        _metric_row(
            "Sessions",
            str(item.sessions),
        )
    )

    progress = ""

    if item.target_progress is not None:

        progress = f"""
            <div class="weekly-summary-progress">
                <div class="weekly-summary-track">
                    <div
                        class="weekly-summary-fill"
                        style="width: {item.target_progress}%"
                    ></div>
                </div>
                <span>
                    {item.target_progress}% of target
                </span>
            </div>
        """

    return f"""
        <section class="weekly-summary-sport">
            <header>
                <span class="weekly-summary-icon">
                    {_SPORT_ICONS[item.sport]}
                </span>
                <strong>
                    {escape(item.sport)}
                </strong>
            </header>

            <div class="weekly-summary-rows">
                {''.join(rows)}
            </div>

            {progress}
        </section>
    """


def weekly_summary_card(
    data: WeeklySummaryCardData,
) -> None:
    """
    Render the weekly multisport summary card.
    """

    if not data.sports:

        components.html(
            """
            <div style="
                color: rgba(49, 51, 63, 0.64);
                font-family: sans-serif;
                font-size: 0.82rem;
            ">
                No training sessions this week.
            </div>
            """,
            height=48,
        )

        return

    sport_blocks = "".join(
        _sport_block(item)
        for item in data.sports
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

                .weekly-summary-list {{
                    display: flex;
                    flex-direction: column;
                    gap: 0.65rem;
                }}

                .weekly-summary-sport {{
                    padding: 0.8rem 0.85rem;
                    border-radius: 0.55rem;
                    background: rgba(49, 51, 63, 0.035);
                }}

                .weekly-summary-sport header {{
                    display: flex;
                    align-items: center;
                    gap: 0.55rem;
                    margin-bottom: 0.65rem;
                    font-size: 0.86rem;
                }}

                .weekly-summary-icon {{
                    display: flex;
                    width: 1.45rem;
                    height: 1.45rem;
                    align-items: center;
                    justify-content: center;
                }}

                .weekly-summary-icon svg {{
                    width: 1.35rem;
                    height: 1.35rem;
                    fill: none;
                    stroke: currentColor;
                    stroke-width: 1.65;
                    stroke-linecap: round;
                    stroke-linejoin: round;
                }}

                .weekly-summary-rows {{
                    display: flex;
                    flex-direction: column;
                    gap: 0.28rem;
                }}

                .weekly-summary-row {{
                    display: flex;
                    align-items: baseline;
                    justify-content: space-between;
                    gap: 1rem;
                    font-size: 0.78rem;
                    line-height: 1.35;
                }}

                .weekly-summary-row span {{
                    color: rgba(49, 51, 63, 0.7);
                }}

                .weekly-summary-row strong {{
                    font-weight: 620;
                    white-space: nowrap;
                }}

                .weekly-summary-progress {{
                    margin-top: 0.65rem;
                }}

                .weekly-summary-track {{
                    width: 100%;
                    height: 0.34rem;
                    overflow: hidden;
                    border: 1px solid rgba(49, 51, 63, 0.2);
                    border-radius: 999px;
                    background: transparent;
                }}

                .weekly-summary-fill {{
                    height: 100%;
                    border-radius: inherit;
                    background: #31333f;
                }}

                .weekly-summary-progress span {{
                    display: block;
                    margin-top: 0.28rem;
                    color: rgba(49, 51, 63, 0.7);
                    font-size: 0.7rem;
                }}
            </style>
        </head>

        <body>
            <div class="weekly-summary-list">
                {sport_blocks}
            </div>
        </body>
        </html>
        """
    ).strip()

    height = (
        48
        + len(data.sports) * 185
    )

    components.html(
        html,
        height=height,
        scrolling=False,
    )