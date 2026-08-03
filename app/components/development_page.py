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
        "Understand how training load is influencing "
        "fitness, fatigue, form and recovery."
    )

    development = (
        DevelopmentPresenter(
            athlete
        ).build()
    )

    (
        fitness_column,
        fatigue_column,
        form_column,
        recovery_column,
    ) = st.columns(4)

    with fitness_column:

        st.metric(
            "Fitness",
            (
                f"{development.current_fitness:.1f}"
            ),
            help=(
                "Chronic training load. Represents "
                "longer-term training fitness."
            ),
        )

    with fatigue_column:

        st.metric(
            "Fatigue",
            (
                f"{development.current_fatigue:.1f}"
            ),
            help=(
                "Acute training load. Represents "
                "recent accumulated fatigue."
            ),
        )

    with form_column:

        st.metric(
            "Form",
            (
                f"{development.current_form:+.1f}"
            ),
            help=(
                "Training stress balance. Positive "
                "values generally indicate freshness."
            ),
        )

    with recovery_column:

        st.metric(
            "Recovery",
            (
                f"{development.recovery_score:.0f}"
            ),
            help=(
                "Current recovery score calculated "
                "from the athlete's training state."
            ),
        )

    st.divider()

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