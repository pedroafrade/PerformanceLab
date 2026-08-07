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
            height=190,
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
            height=290,
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
        gap: 0.75rem;
        margin: 0.8rem 0 1rem 0;
    }

    .development-kpi-card {
        display: grid;
        grid-template-columns: 3.2rem minmax(0, 1fr);
        gap: 0.7rem;
        align-items: center;
        min-height: 7.1rem;
        padding: 0.85rem 0.9rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.65rem;
        background: rgba(128, 128, 128, 0.015);
        box-sizing: border-box;
    }

    .development-kpi-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 3rem;
        height: 3rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 50%;
        background: rgba(128, 128, 128, 0.025);
        font-size: 1.35rem;
        font-weight: 500;
    }

    .development-kpi-content {
        min-width: 0;
    }

    .development-kpi-label {
        margin-bottom: 0.18rem;
        font-size: 0.72rem;
        opacity: 0.65;
    }

    .development-kpi-value {
        margin-bottom: 0.08rem;
        font-size: 1.45rem;
        font-weight: 750;
        line-height: 1.05;
    }

    .development-kpi-status {
        overflow: hidden;
        font-size: 0.76rem;
        font-weight: 650;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .development-kpi-context {
        margin-top: 0.45rem;
        overflow: hidden;
        font-size: 0.61rem;
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
        min-height: 21rem;
        padding: 0.9rem 1rem;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.65rem;
        background: rgba(128, 128, 128, 0.012);
        box-sizing: border-box;
    }

    .development-interpretation-heading {
        margin-bottom: 0.7rem;
        font-size: 0.92rem;
        font-weight: 750;
    }

    .development-interpretation-summary {
        margin-bottom: 0.75rem;
        padding: 0.62rem 0.7rem;
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
        grid-template-columns: 1.6rem minmax(0, 1fr);
        gap: 0.55rem;
        align-items: start;
        padding: 0.48rem 0;
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
        margin-top: 0.72rem;
        padding: 0.55rem 0.65rem;
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

def show_development_page(
    athlete,
) -> None:
    """
    Displays the athlete's physiological and
    training-load development.
    """

    st.title(
        "Development"
    )

    st.caption(
        "Training trends, load and performance."
    )

    development = (
        DevelopmentPresenter(
            athlete
        ).build()
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

    chart_column, interpretation_column = (
        st.columns(
            [2.15, 1],
            gap="medium",
        )
    )

    with chart_column:

        st.subheader(
            "Load and form"
        )

        st.caption(
            "Acute load (ATL), chronic load (CTL) "
            "and training stress balance (TSB)."
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

    st.divider()

    st.subheader(
        "Daily training load"
    )

    st.caption(
        "Session-RPE load by day with a "
        "7-day rolling average."
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