"""
PerformanceLab

Athlete development page.
"""

from html import escape

import altair as alt
import streamlit as st

from performancelab.presentation import (
    DevelopmentPresenter,
)


def _development_chart_rows(
    development,
) -> list[dict]:
    """
    Converts immutable development series into rows
    understood by Streamlit charts.
    """

    return [
        {
            "Date": day,
            "Fitness": fitness,
            "Fatigue": fatigue,
            "Form": form,
        }
        for (
            day,
            fitness,
            fatigue,
            form,
        ) in zip(
            development.dates,
            development.fitness,
            development.fatigue,
            development.form,
            strict=True,
        )
    ]


def _daily_load_chart_rows(
    development,
) -> list[dict]:
    """
    Converts daily training load into chart rows.
    """

    return [
        {
            "Date": day,
            "Training load": load,
        }
        for day, load in zip(
            development.dates,
            development.daily_load,
            strict=True,
        )
    ]

def _daily_training_load_chart(
    development,
):
    """
    Builds daily training load with a rolling
    seven-day average.
    """

    rows = (
        _daily_load_chart_rows(
            development
        )
    )

    chart_rows = [
        {
            **row,
            "Date": (
                row["Date"]
                .isoformat()
            ),
        }
        for row in rows
    ]

    base = (
        alt.Chart(
            alt.Data(
                values=chart_rows
            )
        )
        .transform_window(
            rolling_load=(
                "mean(Training load)"
            ),
            frame=[
                -6,
                0,
            ],
            sort=[
                {
                    "field": "Date",
                    "order": "ascending",
                }
            ],
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                axis=alt.Axis(
                    format="%d %b",
                    labelAngle=0,
                    grid=False,
                    tickCount=10,
                ),
            )
        )
    )

    bars = (
        base
        .mark_bar(
            opacity=0.42,
            size=4,
        )
        .encode(
            y=alt.Y(
                "Training load:Q",
                title="Daily load (AU)",
                axis=alt.Axis(
                    orient="left",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Training load:Q",
                    title="Daily load",
                    format=".0f",
                ),
                alt.Tooltip(
                    "rolling_load:Q",
                    title="7-day average",
                    format=".0f",
                ),
            ],
        )
    )

    rolling_line = (
        base
        .mark_line(
            strokeWidth=2,
            opacity=0.72,
        )
        .encode(
            y=alt.Y(
                "rolling_load:Q",
                title="Daily load (AU)",
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "rolling_load:Q",
                    title="7-day average",
                    format=".0f",
                ),
            ],
        )
    )

    return (
        alt.layer(
            bars,
            rolling_line,
        )
        .properties(
            height=175,
        )
        .configure_view(
            strokeWidth=0,
        )
        .configure_axis(
            labelFontSize=10,
            titleFontSize=11,
            gridColor=(
                "rgba(128,128,128,0.14)"
            ),
            domain=False,
            tickColor=(
                "rgba(128,128,128,0.22)"
            ),
        )
    )

def _development_load_form_chart(
    development,
):
    """
    Builds the main ATL, CTL and TSB development chart.
    """

    rows = (
        _development_chart_rows(
            development
        )
    )

    chart_rows = [
        {
            **row,
            "Date": (
                row["Date"]
                .isoformat()
            ),
        }
        for row in rows
    ]

    base = (
        alt.Chart(
            alt.Data(
                values=chart_rows
            )
        )
        .encode(
            x=alt.X(
                "Date:T",
                title=None,
                axis=alt.Axis(
                    format="%d %b",
                    labelAngle=0,
                    grid=False,
                    tickCount=10,
                ),
            )
        )
    )

    load_lines = (
        base
        .transform_fold(
            [
                "Fatigue",
                "Fitness",
            ],
            as_=[
                "Metric",
                "Value",
            ],
        )
        .mark_line(
            strokeWidth=2,
        )
        .encode(
            y=alt.Y(
                "Value:Q",
                title="Load (ATL / CTL)",
                axis=alt.Axis(
                    orient="left",
                ),
                scale=alt.Scale(
                    zero=False,
                ),
            ),
            color=alt.Color(
                "Metric:N",
                title=None,
                scale=alt.Scale(
                    domain=[
                        "Fatigue",
                        "Fitness",
                    ],
                    range=[
                        "#ff4b4b",
                        "#4f86f7",
                    ],
                ),
                legend=alt.Legend(
                    orient="top",
                    direction="horizontal",
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Metric:N",
                    title="Metric",
                ),
                alt.Tooltip(
                    "Value:Q",
                    title="Load",
                    format=".1f",
                ),
            ],
        )
    )

    form_line = (
        base
        .mark_line(
            strokeWidth=2,
            color="#7c3aed",
        )
        .encode(
            y=alt.Y(
                "Form:Q",
                title="Form (TSB)",
                axis=alt.Axis(
                    orient="right",
                ),
                scale=alt.Scale(
                    zero=False,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Date:T",
                    title="Date",
                    format="%d %b %Y",
                ),
                alt.Tooltip(
                    "Form:Q",
                    title="Form (TSB)",
                    format="+.1f",
                ),
                alt.Tooltip(
                    "Fatigue:Q",
                    title="Fatigue (ATL)",
                    format=".1f",
                ),
                alt.Tooltip(
                    "Fitness:Q",
                    title="Fitness (CTL)",
                    format=".1f",
                ),
            ],
        )
    )

    zero_line = (
        alt.Chart(
            alt.Data(
                values=[
                    {
                        "y": 0,
                    }
                ]
            )
        )
        .mark_rule(
            strokeDash=[
                4,
                4,
            ],
            opacity=0.28,
        )
        .encode(
            y="y:Q",
        )
    )

    return (
        alt.layer(
            load_lines,
            form_line,
            zero_line,
        )
        .resolve_scale(
            y="independent"
        )
        .properties(
            height=225,
        )
        .configure_view(
            strokeWidth=0,
        )
        .configure_axis(
            labelFontSize=10,
            titleFontSize=11,
            gridColor=(
                "rgba(128,128,128,0.14)"
            ),
            domain=False,
            tickColor=(
                "rgba(128,128,128,0.22)"
            ),
        )
        .configure_legend(
            labelFontSize=10,
            symbolStrokeWidth=3,
        )
    )

def _form_status(
    value: float,
) -> str:
    """
    Returns a concise current-form interpretation.
    """

    if value >= 5:
        return "Fresh"

    if value >= -5:
        return "Balanced"

    if value >= -15:
        return "Loaded"

    return "Fatigued"


def _recovery_status(
    score: float,
) -> str:
    """
    Returns a concise recovery interpretation.
    """

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Moderate"

    return "Low"


def _load_status(
    acute_load: float,
    chronic_load: float,
) -> str:
    """
    Describes recent load relative to chronic load.
    """

    if chronic_load <= 0:

        return "No baseline"

    ratio = (
        acute_load
        / chronic_load
    )

    if ratio > 1.2:
        return "Elevated"

    if ratio < 0.8:
        return "Reduced"

    return "Stable"


def _development_summary_cards_html(
    development,
) -> str:
    """
    Builds the four development summary cards.
    """

    cards = (
        (
            "♡",
            "Recovery",
            f"{development.recovery_score:.0f}",
            _recovery_status(
                development.recovery_score
            ),
            "Current",
        ),
        (
            "↗",
            "Chronic load",
            f"{development.chronic_load:.0f}",
            _load_status(
                development.acute_load,
                development.chronic_load,
            ),
            "Current training state",
        ),
        (
            "⚖",
            "Form",
            f"{development.current_form:+.1f}",
            _form_status(
                development.current_form
            ),
            "Today",
        ),
        (
            "▥",
            "Acute load",
            f"{development.acute_load:.0f}",
            development.load_status,
            "Recent training load",
        ),
    )

    cards_html = []

    for (
        icon,
        label,
        value,
        status,
        context,
    ) in cards:

        cards_html.append(
            (
                '<section class="development-kpi-card">'
                '<div class="development-kpi-icon">'
                f"{icon}"
                "</div>"
                '<div class="development-kpi-content">'
                '<div class="development-kpi-label">'
                f"{label}"
                "</div>"
                '<div class="development-kpi-value">'
                f"{value}"
                "</div>"
                '<div class="development-kpi-status">'
                f"{status}"
                "</div>"
                '<div class="development-kpi-context">'
                f"{context}"
                "</div>"
                "</div>"
                "</section>"
            )
        )

    return (
        '<div class="development-kpi-grid">'
        + "".join(
            cards_html
        )
        + "</div>"
    )


def _development_summary_styles() -> str:
    """
    Returns styles for the development summary cards.
    """

    return """
    .development-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.65rem;
        margin: 0 0 0.15rem 0;
    }

    .development-kpi-card {
        display: grid;
        grid-template-columns: 2.65rem minmax(0, 1fr);
        gap: 0.6rem;
        align-items: center;
        min-height: 4.65rem;
        padding: 0.34rem 0.7rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.65rem;
        background: rgba(128, 128, 128, 0.015);
        box-sizing: border-box;
    }

    .development-kpi-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.4rem;
        height: 2.4rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 50%;
        background: rgba(128, 128, 128, 0.025);
        font-size: 1.02rem;
        font-weight: 500;
    }

    .development-kpi-content {
        min-width: 0;
    }

    .development-kpi-label {
        margin-bottom: 0.1rem;
        font-size: 0.7rem;
        opacity: 0.65;
    }

    .development-kpi-value {
        margin-bottom: 0.03rem;
        font-size: 1.2rem;
        font-weight: 750;
        line-height: 1;
    }

    .development-kpi-status {
        overflow: hidden;
        font-size: 0.74rem;
        font-weight: 650;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .development-kpi-context {
        margin-top: 0.14rem;
        overflow: hidden;
        font-size: 0.59rem;
        opacity: 0.48;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    @media (max-width: 1050px) {
        .development-kpi-grid {
            grid-template-columns:
                repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 700px) {
        .development-kpi-grid {
            grid-template-columns:
                minmax(0, 1fr);
        }
    }
    """

def _sport_volume_duration_label(
    duration_seconds: float,
) -> str:
    """
    Formats aggregated sport duration.
    """

    total_minutes = round(
        duration_seconds
        / 60
    )

    hours, minutes = divmod(
        total_minutes,
        60,
    )

    if hours and minutes:

        return (
            f"{hours}h {minutes:02d}m"
        )

    if hours:

        return f"{hours}h"

    return f"{minutes}m"

def _pace_label(
    pace: float | None,
) -> str:
    """
    Formats minutes per kilometre as mm:ss /km.
    """

    if (
        pace is None
        or pace <= 0
    ):

        return "—"

    total_seconds = round(
        pace * 60
    )

    minutes, seconds = divmod(
        total_seconds,
        60,
    )

    return (
        f"{minutes}:{seconds:02d} /km"
    )

def _development_sport_volume_html(
    development,
) -> str:
    """
    Builds the compact volume-by-sport card.
    """

    rows = tuple(
        development.sport_volume
    )

    if not rows:

        return (
            '<section class="development-volume-card">'
            '<div class="development-volume-heading">'
            "Volume by sport"
            "</div>"
            '<div class="development-volume-empty">'
            "No completed activity volume."
            "</div>"
            "</section>"
        )

    maximum_duration = max(
        (
            row.duration_seconds
            for row in rows
        ),
        default=0.0,
    )

    row_html = []

    for row in rows[:3]:

        if maximum_duration > 0:

            percentage = (
                row.duration_seconds
                / maximum_duration
                * 100
            )

        else:

            percentage = 0.0

        duration_label = (
            _sport_volume_duration_label(
                row.duration_seconds
            )
        )

        distance_label = (
            f"{row.distance:.0f} km"
            if row.distance > 0
            else "—"
        )

        row_html.append(
            (
                '<div class="development-volume-row">'
                '<div class="development-volume-row-top">'
                '<span class="development-volume-sport">'
                f"{escape(row.sport)}"
                "</span>"
                '<span class="development-volume-value">'
                f"{escape(duration_label)}"
                " · "
                f"{escape(distance_label)}"
                "</span>"
                "</div>"
                '<div class="development-volume-track">'
                '<div class="development-volume-fill" '
                f'style="width:{percentage:.1f}%">'
                "</div>"
                "</div>"
                "</div>"
            )
        )

    total_seconds = sum(
        row.duration_seconds
        for row in rows
    )

    total_distance = sum(
        row.distance
        for row in rows
    )

    total_sessions = sum(
        row.sessions
        for row in rows
    )

    total_duration = (
        _sport_volume_duration_label(
            total_seconds
        )
    )

    return (
        '<section class="development-volume-card">'
        '<div class="development-volume-heading">'
        "Volume by sport"
        "</div>"
        '<div class="development-volume-subtitle">'
        "Completed activity history"
        "</div>"
        '<div class="development-volume-rows">'
        + "".join(
            row_html
        )
        + "</div>"
        '<div class="development-volume-total">'
        '<span>Total</span>'
        "<span>"
        f"{escape(total_duration)}"
        " · "
        f"{total_distance:.0f} km"
        " · "
        f"{total_sessions} sessions"
        "</span>"
        "</div>"
        "</section>"
    )

def _development_intensity_html(
    development,
) -> str:
    """
    Builds heart-rate zone distribution and RPE summary.
    """

    intensity = (
        development.intensity
    )

    if intensity is None:

        return (
            '<section class="development-intensity-card">'
            '<div class="development-intensity-heading">'
            "Intensity & RPE"
            "</div>"
            '<div class="development-intensity-empty">'
            "No intensity data available."
            "</div>"
            "</section>"
        )

    zone_rows = []

    for zone in intensity.zones:

        duration = (
            _sport_volume_duration_label(
                zone.duration_seconds
            )
        )

        zone_rows.append(
            (
                '<div class="development-zone-row">'
                '<span class="development-zone-name">'
                f"{escape(zone.name)}"
                "</span>"
                '<div class="development-zone-track">'
                '<div class="development-zone-fill" '
                f'style="width:{zone.percentage:.1f}%">'
                "</div>"
                "</div>"
                '<span class="development-zone-percent">'
                f"{zone.percentage:.0f}%"
                "</span>"
                '<span class="development-zone-time">'
                f"{escape(duration)}"
                "</span>"
                "</div>"
            )
        )

    average_rpe = (
        (
            f"{intensity.average_rpe:.1f}"
        )
        if intensity.average_rpe
        is not None
        else "—"
    )

    source_label = {
        "manual": "Manual HR zones",
        "karvonen": "Karvonen HR zones",
    }.get(
        intensity.zone_source,
        "Heart-rate zones",
    )

    return (
        '<section class="development-intensity-card">'
        '<div class="development-intensity-heading">'
        "Intensity & RPE"
        "</div>"
        '<div class="development-intensity-subtitle">'
        f"{escape(source_label)}"
        "</div>"
        '<div class="development-zone-rows">'
        + "".join(
            zone_rows
        )
        + "</div>"
        '<div class="development-intensity-metrics">'
        '<div>'
        '<span>Average RPE</span>'
        '<strong>'
        f"{average_rpe}"
        "</strong>"
        "</div>"
        '<div>'
        '<span>RPE &gt; 8</span>'
        '<strong>'
        f"{intensity.high_rpe_sessions}"
        "</strong>"
        "</div>"
        "</div>"
        "</section>"
    )

def _development_performance_references_html(
    development,
) -> str:
    """
    Builds running pace and threshold references.
    """

    references = (
        development
        .performance_references
    )

    if references is None:

        return (
            '<section class="development-reference-card">'
            '<div class="development-reference-heading">'
            "Pace & thresholds"
            "</div>"
            '<div class="development-reference-empty">'
            "No performance references available."
            "</div>"
            "</section>"
        )

    zone_rows = []

    for zone in references.pace_zones:

        pace_range = (
            f"{_pace_label(zone.faster_pace)}"
            " – "
            f"{_pace_label(zone.slower_pace)}"
        )

        zone_rows.append(
            (
                '<div class="development-reference-row">'
                '<span class="development-reference-label">'
                f"{escape(zone.name)}"
                "</span>"
                '<strong class="development-reference-value">'
                f"{escape(pace_range)}"
                "</strong>"
                "</div>"
            )
        )

    threshold_rows = (
        (
            "Easy pace",
            _pace_label(
                references.easy_pace
            ),
        ),
        (
            "Tempo",
            _pace_label(
                references.tempo_pace
            ),
        ),
        (
            "LT2 pace",
            _pace_label(
                references.lt2_pace
            ),
        ),
        (
            "Threshold HR",
            (
                f"{references.threshold_hr} bpm"
                if references.threshold_hr
                is not None
                else "—"
            ),
        ),
    )

    if references.ftp is not None:

        threshold_rows = (
            *threshold_rows,
            (
                "FTP",
                f"{references.ftp:.0f} W",
            ),
        )

    summary_html = []

    for (
        label,
        value,
    ) in threshold_rows:

        summary_html.append(
            (
                '<div class="development-reference-summary-row">'
                '<span>'
                f"{escape(label)}"
                "</span>"
                "<strong>"
                f"{escape(value)}"
                "</strong>"
                "</div>"
            )
        )

    return (
        '<section class="development-reference-card">'
        '<div class="development-reference-heading">'
        "Pace & thresholds"
        "</div>"
        '<div class="development-reference-subtitle">'
        "Running pace zones and thresholds"
        "</div>"
        '<div class="development-reference-zones">'
        + "".join(
            zone_rows
        )
        + "</div>"
        '<div class="development-reference-summary">'
        + "".join(
            summary_html
        )
        + "</div>"
        "</section>"
    )

def _development_overall_status(
    development,
) -> tuple[str, str]:
    """
    Returns the headline interpretation of the
    current training state.
    """

    load_status = (
        _load_status(
            development.acute_load,
            development.chronic_load,
        )
    )

    recovery_status = (
        _recovery_status(
            development.recovery_score
        )
    )

    form_status = (
        _form_status(
            development.current_form
        )
    )

    if (
        recovery_status == "Low"
        or form_status == "Fatigued"
    ):

        return (
            "Recovery deserves attention",
            (
                "The current state suggests that "
                "recovery should take priority."
            ),
        )

    if load_status == "Elevated":

        return (
            "Training load is elevated",
            (
                "Recent load is above the current "
                "chronic training baseline."
            ),
        )

    if (
        recovery_status == "Good"
        and form_status
        in {
            "Fresh",
            "Balanced",
        }
    ):

        return (
            "Training state is balanced",
            (
                "Load, recovery and form are currently "
                "well balanced."
            ),
        )

    return (
        "Training state is manageable",
        (
            "The current metrics remain within a "
            "manageable training state."
        ),
    )


def _development_interpretation_html(
    development,
) -> str:
    """
    Builds the current training interpretation panel.
    """

    (
        headline,
        headline_detail,
    ) = _development_overall_status(
        development
    )

    load_status = (
        _load_status(
            development.acute_load,
            development.chronic_load,
        )
    )

    recovery_status = (
        _recovery_status(
            development.recovery_score
        )
    )

    form_status = (
        _form_status(
            development.current_form
        )
    )

    load_detail = (
        f"Acute {development.acute_load:.0f} AU"
        " · "
        f"chronic {development.chronic_load:.0f} AU"
    )

    recovery_detail = (
        f"{development.recovery_score:.0f}/100"
        " · "
        f"{development.recovery_status}"
    )

    form_detail = (
        f"{development.current_form:+.1f} TSB"
    )

    recommendation = (
        development.load_recommendation
        or development.recovery_recommendation
        or "Maintain the current training progression."
    )

    items = (
        (
            "↗",
            "Training load",
            load_status,
            load_detail,
        ),
        (
            "♡",
            "Recovery",
            recovery_status,
            recovery_detail,
        ),
        (
            "⚖",
            "Form",
            form_status,
            form_detail,
        ),
    )

    item_html = []

    for (
        icon,
        label,
        status,
        detail,
    ) in items:

        item_html.append(
            (
                '<div class="development-interpretation-item">'
                '<div class="development-interpretation-icon">'
                f"{icon}"
                "</div>"
                '<div class="development-interpretation-copy">'
                '<div class="development-interpretation-label">'
                f"{escape(label)}"
                "</div>"
                '<div class="development-interpretation-status">'
                f"{escape(str(status))}"
                "</div>"
                '<div class="development-interpretation-detail">'
                f"{escape(str(detail))}"
                "</div>"
                "</div>"
                "</div>"
            )
        )

    return (
        '<section class="development-interpretation-card">'
        '<div class="development-interpretation-heading">'
        "Interpretation"
        "</div>"
        '<div class="development-interpretation-summary">'
        '<div class="development-interpretation-summary-title">'
        f"{escape(headline)}"
        "</div>"
        '<div class="development-interpretation-summary-detail">'
        f"{escape(headline_detail)}"
        "</div>"
        "</div>"
        '<div class="development-interpretation-items">'
        + "".join(
            item_html
        )
        + "</div>"
        '<div class="development-interpretation-recommendation">'
        '<div class="development-interpretation-recommendation-label">'
        "Recommendation"
        "</div>"
        '<div class="development-interpretation-recommendation-text">'
        f"{escape(str(recommendation))}"
        "</div>"
        "</div>"
        "</section>"
    )


def _development_interpretation_styles() -> str:
    """
    Returns styles for the interpretation panel.
    """

    return """
    .development-interpretation-card {
        height: 100%;
        min-height: 15.5rem;
        padding: 0.55rem 0.7rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.65rem;
        background: rgba(128, 128, 128, 0.012);
        box-sizing: border-box;
    }

    .development-interpretation-heading {
        margin-bottom: 0.45rem;
        font-size: 0.92rem;
        font-weight: 750;
    }

    .development-interpretation-summary {
        margin-bottom: 0.4rem;
        padding: 0.45rem 0.55rem;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 0.5rem;
        background: rgba(128, 128, 128, 0.025);
    }

    .development-interpretation-summary-title {
        margin-bottom: 0.14rem;
        font-size: 0.82rem;
        font-weight: 750;
    }

    .development-interpretation-summary-detail {
        font-size: 0.66rem;
        line-height: 1.35;
        opacity: 0.62;
    }

    .development-interpretation-items {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .development-interpretation-item {
        display: grid;
        grid-template-columns: 1.35rem minmax(0, 1fr);
        gap: 0.42rem;
        align-items: start;
        padding: 0.31rem 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.14);
    }

    .development-interpretation-icon {
        padding-top: 0.08rem;
        font-size: 1rem;
        text-align: center;
    }

    .development-interpretation-copy {
        min-width: 0;
    }

    .development-interpretation-label {
        font-size: 0.64rem;
        opacity: 0.52;
    }

    .development-interpretation-status {
        margin-top: 0.04rem;
        font-size: 0.76rem;
        font-weight: 700;
    }

    .development-interpretation-detail {
        margin-top: 0.08rem;
        overflow: hidden;
        font-size: 0.63rem;
        line-height: 1.3;
        opacity: 0.58;
        text-overflow: ellipsis;
    }

    .development-interpretation-recommendation {
        margin-top: 0.4rem;
        padding: 0.4rem 0.5rem;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 0.45rem;
    }

    .development-interpretation-recommendation-label {
        margin-bottom: 0.16rem;
        font-size: 0.62rem;
        font-weight: 750;
        opacity: 0.58;
        text-transform: uppercase;
    }

    .development-interpretation-recommendation-text {
        font-size: 0.68rem;
        line-height: 1.35;
    }
    """

def _development_lower_styles() -> str:
    """
    Returns styles for lower development cards.
    """

    return """
.development-volume-card,
.development-intensity-card,
.development-reference-card {
    height: 9.1rem;
    padding: 0.48rem 0.6rem 0.42rem;
    border: 1px solid rgba(128, 128, 128, 0.22);
    border-radius: 0.65rem;
    background: rgba(128, 128, 128, 0.012);
    box-sizing: border-box;
    overflow: hidden;
}

/* Pace & thresholds needs slightly more vertical room */
.development-reference-card {
    height: 9.35rem;
}

    .development-volume-card,
    .development-intensity-card {
        display: flex;
        flex-direction: column;
    }

    .development-volume-heading,
    .development-intensity-heading,
    .development-reference-heading {
        font-size: 0.88rem;
        line-height: 1.05;
        font-weight: 750;
    }

    .development-volume-subtitle,
    .development-intensity-subtitle,
    .development-reference-subtitle {
        margin-top: 0.02rem;
        margin-bottom: 0.22rem;
        font-size: 0.61rem;
        line-height: 1.1;
        opacity: 0.52;
    }

    /* Volume by sport */

    .development-volume-rows {
        display: flex;
        flex-direction: column;
        gap: 0.24rem;
    }

    .development-volume-row-top {
        display: flex;
        justify-content: space-between;
        gap: 0.4rem;
        margin-bottom: 0.06rem;
        align-items: center;
    }

    .development-volume-sport {
        overflow: hidden;
        font-size: 0.68rem;
        line-height: 1.05;
        font-weight: 650;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .development-volume-value {
        flex: 0 0 auto;
        font-size: 0.62rem;
        line-height: 1.05;
        opacity: 0.6;
        white-space: nowrap;
    }

    .development-volume-track,
    .development-zone-track {
        width: 100%;
        overflow: hidden;
        border-radius: 999px;
        background: rgba(128, 128, 128, 0.14);
    }

    .development-volume-track {
        height: 0.24rem;
    }

    .development-volume-fill,
    .development-zone-fill {
        height: 100%;
        border-radius: inherit;
        background: currentColor;
        opacity: 0.52;
    }

    .development-volume-total {
        display: flex;
        justify-content: space-between;
        gap: 0.35rem;
        margin-top: auto;
        padding-top: 0.24rem;
        border-top: 1px solid rgba(128, 128, 128, 0.14);
        font-size: 0.61rem;
        line-height: 1.05;
        font-weight: 650;
    }

    /* Intensity & RPE */

    .development-zone-rows {
        display: flex;
        flex-direction: column;
        gap: 0.13rem;
    }

    .development-zone-row {
        display: grid;
        grid-template-columns:
            1.25rem minmax(0, 1fr) 1.7rem 2.2rem;
        gap: 0.22rem;
        align-items: center;
        min-width: 0;
    }

    .development-zone-name {
        font-size: 0.64rem;
        line-height: 1.05;
        font-weight: 700;
    }

    .development-zone-track {
        height: 0.28rem;
    }

    .development-zone-percent,
    .development-zone-time {
        font-size: 0.58rem;
        line-height: 1.05;
        opacity: 0.62;
        text-align: right;
        white-space: nowrap;
    }

    .development-intensity-metrics {
        display: grid;
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
        gap: 0.4rem;
        margin-top: auto;
        padding-top: 0.2rem;
        border-top: 1px solid rgba(128, 128, 128, 0.14);
    }

    .development-intensity-metrics div {
        display: flex;
        flex-direction: column;
        gap: 0;
    }

    .development-intensity-metrics span {
        font-size: 0.57rem;
        line-height: 1.05;
        opacity: 0.55;
    }

    .development-intensity-metrics strong {
        margin-top: 0.04rem;
        font-size: 0.78rem;
        line-height: 1;
    }

    /* Pace & thresholds */

    .development-reference-zones {
        display: flex;
        flex-direction: column;
        gap: 0.15rem;
    }

    .development-reference-row,
    .development-reference-summary-row {
        display: flex;
        justify-content: space-between;
        gap: 0.4rem;
        align-items: center;
    }

    .development-reference-row {
        font-size: 0.67rem;
        line-height: 1.05;
    }

    .development-reference-label {
        font-weight: 700;
    }

    .development-reference-value {
        font-size: 0.64rem;
        line-height: 1.05;
        font-weight: 600;
        white-space: nowrap;
    }

    .development-reference-summary {
        display: grid;
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
        gap: 0.12rem 0.5rem;
        margin-top: 0.28rem;
        padding-top: 0.24rem;
        border-top: 1px solid rgba(128, 128, 128, 0.14);
    }

    .development-reference-summary-row {
        min-width: 0;
        font-size: 0.61rem;
        line-height: 1.05;
    }

    .development-reference-summary-row span {
        opacity: 0.58;
    }

    .development-reference-summary-row strong {
        font-size: 0.64rem;
        white-space: nowrap;
    }

    .development-volume-empty,
    .development-intensity-empty,
    .development-reference-empty {
        padding-top: 2rem;
        font-size: 0.62rem;
        opacity: 0.55;
        text-align: center;
    }
    """

def _development_chart_heading_html(
    title: str,
    subtitle: str,
) -> str:
    """
    Builds a compact heading for development charts.
    """

    return (
        '<div class="development-chart-heading">'
        '<div class="development-chart-title">'
        f"{escape(title)}"
        "</div>"
        '<div class="development-chart-subtitle">'
        f"{escape(subtitle)}"
        "</div>"
        "</div>"
    )

def show_development_page(
    athlete,
) -> None:
    """
    Displays the athlete's physiological and
    training-load development.
    """

    development = (
        DevelopmentPresenter(
            athlete
        ).build()
    )

    st.markdown(
        """
        <style>
        div[data-testid="stMainBlockContainer"] {
            padding-top: 3.65rem;
            padding-bottom: 0;
        }

        section[data-testid="stMain"] > div {
            padding-bottom: 0 !important;
        }

        div[data-testid="stMainBlockContainer"] > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }

        .development-page-header {
            margin: 0 0 0.45rem 0;
            padding: 0;
        }

        .development-page-title {
            margin: 0;
            font-size: 2.25rem;
            font-weight: 750;
            line-height: 1.05;
        }

        .development-page-subtitle {
            margin-top: 0.32rem;
            font-size: 0.76rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .development-chart-heading {
            margin: 0;
            padding: 0;
        }

        .development-chart-title {
            margin: 0;
            font-size: 1.35rem;
            font-weight: 700;
            line-height: 1.05;
        }

        .development-chart-subtitle {
            margin: 0.14rem 0 0 0;
            font-size: 0.69rem;
            line-height: 1.15;
            opacity: 0.58;
        }

        .development-section-gap {
            height: 0.55rem;
        }

        /* Marker between the two charts. */
        .development-between-charts {
            height: 0;
        }

        /* Collapse the Streamlit element that contains the marker. */
        div[data-testid="stElementContainer"]:has(
            .development-between-charts
        ) {
            height: 0;
            min-height: 0;
            margin-top: -0.65rem;
            margin-bottom: -1.35rem;
        }

        /* Marker immediately before the three lower cards. */
        .development-lower-row {
            height: 0;
        }

        /* Pull the complete lower row upwards. */
        div[data-testid="stElementContainer"]:has(
            .development-lower-row
        ) {
            height: 0;
            min-height: 0;
            margin-top: -0.65rem;
            margin-bottom: -1.55rem;
        }
        </style>

        <div class="development-page-header">
            <div class="development-page-title">
                Development
            </div>
            <div class="development-page-subtitle">
                Training trends, load and performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        (
            "<style>"
            + _development_summary_styles()
            + "</style>"
            + _development_summary_cards_html(
                development
            )
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="development-section-gap"></div>',
        unsafe_allow_html=True,
    )
    (
        chart_column,
        interpretation_column,
    ) = st.columns(
        [2.15, 1],
        gap="medium",
    )

    with chart_column:

        st.markdown(
            _development_chart_heading_html(
                "Load and form",
                (
                    "Acute load (ATL), chronic load (CTL) "
                    "and training stress balance (TSB)."
                ),
            ),
            unsafe_allow_html=True,
        )

        performance_rows = (
            _development_chart_rows(
                development
            )
        )

        if performance_rows:

            st.altair_chart(
                _development_load_form_chart(
                    development
                ),
                use_container_width=True,
            )

        else:

            st.info(
                "Import activity history to calculate "
                "performance development."
            )

        st.markdown(
            '<div class="development-between-charts"></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            _development_chart_heading_html(
                "Daily training load",
                (
                    "Session-RPE load by day with a "
                    "7-day rolling average."
                ),
            ),
            unsafe_allow_html=True,
        )

        load_rows = (
            _daily_load_chart_rows(
                development
            )
        )

        if load_rows:

            st.altair_chart(
                _daily_training_load_chart(
                    development
                ),
                use_container_width=True,
            )

        else:

            st.info(
                "No daily training load is available."
            )

    with interpretation_column:

        st.markdown(
            (
                "<style>"
                + _development_interpretation_styles()
                + "</style>"
                + _development_interpretation_html(
                    development
                )
            ),
            unsafe_allow_html=True,
        )
    st.markdown(
        '<div class="development-lower-row"></div>',
        unsafe_allow_html=True,
    )
    (
        volume_column,
        intensity_column,
        references_column,
    ) = st.columns(
        [1, 1, 1],
        gap="medium",
    )

    with volume_column:

        st.markdown(
            (
                "<style>"
                + _development_lower_styles()
                + "</style>"
                + _development_sport_volume_html(
                    development
                )
            ),
            unsafe_allow_html=True,
        )

    with intensity_column:

        st.markdown(
            (
                "<style>"
                + _development_lower_styles()
                + "</style>"
                + _development_intensity_html(
                    development
                )
            ),
            unsafe_allow_html=True,
        )

    with references_column:

        st.markdown(
            (
                "<style>"
                + _development_lower_styles()
                + "</style>"
                + _development_performance_references_html(
                    development
                )
            ),
            unsafe_allow_html=True,
        )