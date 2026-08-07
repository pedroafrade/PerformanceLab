"""
PerformanceLab

Athlete development page.
"""

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

    st.subheader(
        "Performance development"
    )

    st.caption(
        "Fitness, fatigue and form across the available "
        "training history."
    )

    performance_rows = (
        _development_chart_rows(
            development
        )
    )

    if performance_rows:

        st.line_chart(
            performance_rows,
            x="Date",
            y=[
                "Fitness",
                "Fatigue",
                "Form",
            ],
            use_container_width=True,
        )

    else:

        st.info(
            "Import activity history to calculate "
            "performance development."
        )

    st.divider()

    load_column, guidance_column = (
        st.columns(
            [2, 1]
        )
    )

    with load_column:

        st.subheader(
            "Daily training load"
        )

        st.caption(
            "Session-RPE load accumulated each day."
        )

        load_rows = (
            _daily_load_chart_rows(
                development
            )
        )

        if load_rows:

            st.bar_chart(
                load_rows,
                x="Date",
                y="Training load",
                use_container_width=True,
            )

        else:

            st.info(
                "No daily training load is available."
            )

    with guidance_column:

        st.subheader(
            "Current guidance"
        )

        st.metric(
            "Acute load",
            (
                f"{development.acute_load:.1f}"
            ),
        )

        st.metric(
            "Chronic load",
            (
                f"{development.chronic_load:.1f}"
            ),
        )

        st.metric(
            "Ramp",
            (
                f"{development.ramp_rate:+.1f}%"
            ),
        )

        st.markdown(
            f"**Load status:** "
            f"{development.load_status}"
        )

        st.write(
            development.load_recommendation
        )

    st.divider()

    recovery_column, interpretation_column = (
        st.columns(2)
    )

    with recovery_column:

        st.subheader(
            "Recovery"
        )

        st.markdown(
            f"**Status:** "
            f"{development.recovery_status}"
        )

        st.write(
            development.recovery_recommendation
        )

    with interpretation_column:

        st.subheader(
            "How to read this page"
        )

        st.write(
            "Fitness changes gradually. Fatigue reacts "
            "more quickly to recent training. Form is "
            "the balance between both and should be "
            "interpreted together with recovery and the "
            "planned training context."
        )