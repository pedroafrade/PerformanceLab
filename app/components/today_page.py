"""
PerformanceLab

Today page.
"""

from datetime import timedelta

import streamlit as st

from performancelab.presentation import (
    TodayPresenter,
)

from .dashboard.cards.next_workout_card import (
    next_workout_card,
)
from .dashboard.cards.recovery_card import (
    recovery_card,
)
from .dashboard.cards.training_load_card import (
    training_load_card,
)
from .dashboard.widget import (
    dashboard_widget,
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


def _show_today_session(
    session,
) -> None:
    """
    Displays today's planned or completed session.
    """

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

    st.markdown(
        (
            "**Status:** "
            f"{_today_session_status(session)}"
        )
    )

    if (
        session is None
        or not session.structure
    ):
        return

    st.divider()

    for index, step in enumerate(
        session.structure,
        start=1,
    ):

        st.markdown(
            f"{index}. {step}"
        )


def show_today_page(
    athlete,
):
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

    st.info(
        (
            f"**{today.coach.summary}**\n\n"
            f"{today.coach.recommendation}"
        )
    )

    session_column, next_column = (
        st.columns(
            [1, 1],
            gap="large",
        )
    )

    with session_column:

        with dashboard_widget(
            title="Today's session",
            icon=":material/today:",
            divider=True,
        ):

            _show_today_session(
                today.today_session
            )

    with next_column:

        with dashboard_widget(
            title="Next workout",
            icon=":material/fitness_center:",
            divider=True,
        ):

            next_workout_card(
                today.next_workout
            )

    st.markdown(
        "### Current readiness"
    )

    recovery_column, load_column = (
        st.columns(2)
    )

    with recovery_column:

        with dashboard_widget(
            title="Recovery",
            icon=":material/favorite:",
            divider=False,
        ):

            recovery_card(
                today.recovery
            )

    with load_column:

        with dashboard_widget(
            title="Training load",
            icon=":material/monitoring:",
            divider=False,
        ):

            training_load_card(
                today.training_load
            )

    return None