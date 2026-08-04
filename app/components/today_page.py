"""
PerformanceLab

Today page.
"""

from datetime import timedelta
from html import escape

import streamlit as st

from performancelab.presentation import (
    TodayPresenter,
)


def _duration_label(
    duration: timedelta | None,
) -> str | None:
    """
    Formats a duration for the daily session.
    """

    if duration is None:
        return None

    total_minutes = round(
        duration.total_seconds()
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

    return f"{minutes} min"


def _readiness_score_label(
    value: int,
) -> str:
    """
    Formats the daily recovery score.
    """

    return f"{value}/100"


def _form_label(
    value: float,
) -> str:
    """
    Formats the current physiological form.
    """

    return f"{value:+.1f}"


def _recent_load_label(
    value: float,
) -> str:
    """
    Formats the recent training load.
    """

    return f"{value:.1f}"


def _today_session_title(
    session,
) -> str:
    """
    Returns the most relevant title for today.
    """

    if session is None:
        return "Rest day"

    if session.completed:
        return (
            session.completed_title
            or session.title
            or "Completed activity"
        )

    return (
        session.title
        or "Rest day"
    )


def _today_session_status(
    session,
) -> str:
    """
    Returns a readable daily session status.
    """

    if session is None:
        return "No planned training"

    if session.outcome_status:
        return (
            session.outcome_status
            .replace("_", " ")
            .title()
        )

    if session.completed:
        return "Completed"

    if session.title:
        return "Planned"

    return "Recovery"


def _today_session_metadata(
    session,
) -> str:
    """
    Returns concise session metadata.
    """

    if session is None:
        return "No training is planned."

    values = [
        value
        for value in (
            (
                session.completed_sport
                if session.completed
                else session.sport
            ),
            _duration_label(
                session.duration
            ),
            session.intensity,
        )
        if value
    ]

    if not values:
        return (
            "Use today for recovery "
            "and preparation."
        )

    return " · ".join(
        values
    )


def _session_step_html(
    *,
    index: int,
    step: str,
) -> str:
    """
    Builds one monochrome executable session row.
    """

    return (
        "<div style='"
        "display:grid;"
        "grid-template-columns:1.55rem minmax(0,1fr);"
        "align-items:center;"
        "gap:0.65rem;"
        "padding:0.62rem 0.15rem;"
        "border-bottom:1px solid rgba(128,128,128,0.22);"
        "'>"
        "<span style='"
        "display:flex;"
        "align-items:center;"
        "justify-content:center;"
        "width:1.35rem;"
        "height:1.35rem;"
        "border:1px solid rgba(128,128,128,0.45);"
        "border-radius:50%;"
        "font-size:0.72rem;"
        "font-weight:600;"
        "'>"
        f"{index}"
        "</span>"
        "<span style='"
        "font-size:0.88rem;"
        "line-height:1.35;"
        "'>"
        f"{escape(step)}"
        "</span>"
        "</div>"
    )


def _show_today_session(
    session,
) -> None:
    """
    Displays today's session as the dominant action.
    """

    with st.container(
        border=True
    ):
        st.markdown(
            "**Today's session**"
        )

        st.subheader(
            _today_session_title(
                session
            )
        )

        st.caption(
            _today_session_metadata(
                session
            )
        )

        if (
            session is not None
            and session.structure
        ):
            steps = "".join(
                _session_step_html(
                    index=index,
                    step=step,
                )
                for index, step in enumerate(
                    session.structure,
                    start=1,
                )
            )

            st.html(
                (
                    "<div style='"
                    "margin-top:0.55rem;"
                    "border-top:1px solid "
                    "rgba(128,128,128,0.22);"
                    "'>"
                    f"{steps}"
                    "</div>"
                )
            )

        st.caption(
            (
                "Status · "
                f"{_today_session_status(session)}"
            )
        )


def _show_daily_decision(
    today,
) -> None:
    """
    Displays the daily decision and the minimum
    physiological context required to understand it.
    """

    with st.container(
        border=True
    ):
        (
            decision_column,
            recovery_column,
            form_column,
            load_column,
        ) = st.columns(
            [3.4, 1, 1, 1],
            gap="medium",
            vertical_alignment="center",
        )

        with decision_column:
            st.markdown(
                f"### {today.coach.summary}"
            )

            st.caption(
                today.coach.recommendation
            )

        with recovery_column:
            st.metric(
                label="Recovery",
                value=_readiness_score_label(
                    today.readiness
                    .recovery_score
                ),
            )

            st.caption(
                today.readiness
                .recovery_status
            )

        with form_column:
            st.metric(
                label="Form",
                value=_form_label(
                    today.readiness.form
                ),
            )

        with load_column:
            st.metric(
                label="Recent load",
                value=_recent_load_label(
                    today.readiness
                    .recent_load
                ),
            )


def show_today_page(
    athlete,
) -> None:
    """
    Displays the athlete's daily decision page.
    """

    today = TodayPresenter(
        athlete
    ).build()

    st.title(
        "Today"
    )

    st.caption(
        today.reference_day.strftime(
            "%A, %d %B %Y"
        )
    )

    _show_daily_decision(
        today
    )

    _show_today_session(
        today.today_session
    )
