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
from .dashboard.cards.latest_activity_card import (
    latest_activity_card,
)
from .dashboard.cards.next_event_card import (
    next_event_card,
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


def _outcome_label(
    status: str | None,
) -> str:
    """
    Returns a readable activity outcome.
    """

    labels = {
        "equivalent": "Equivalent",
        "modified": "Modified",
        "substitute": "Substitute",
        "unplanned": "Unplanned",
        "outside_plan": "Outside plan",
    }

    if status is None:
        return "Not compared"

    return labels.get(
        status,
        status.replace(
            "_",
            " ",
        ).title(),
    )


def _activity_outcome_summary(
    activity,
) -> str:
    """
    Summarises how the latest activity compared
    with the plan.
    """

    if activity is None:
        return (
            "No recent activity is available."
        )

    parts = [
        _outcome_label(
            activity.outcome_status
        )
    ]

    if activity.planned_title:

        parts.append(
            (
                "Planned: "
                f"{activity.planned_title}"
            )
        )

    if (
        activity.load_difference
        is not None
    ):

        parts.append(
            (
                "Load difference: "
                f"{activity.load_difference:+.0f} AU"
            )
        )

    return " · ".join(
        parts
    )


def _show_empty_state(
    *,
    title: str,
    message: str,
) -> None:
    """
    Displays a consistent empty state inside a
    Today page widget.
    """

    st.markdown(
        f"**{title}**"
    )

    st.caption(
        message
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
            vertical_alignment="top",
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

            if today.next_workout is None:

                _show_empty_state(
                    title="No upcoming workout",
                    message=(
                        "There is no future training "
                        "session in the current plan."
                    ),
                )

            else:

                next_workout_card(
                    today.next_workout
                )

    st.markdown(
        "### Current readiness"
    )

    recovery_column, load_column = (
        st.columns(
            2,
            gap="large",
            vertical_alignment="top",
        )
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

    st.markdown(
        "### Recent context"
    )

    activity_column, event_column = (
        st.columns(
            [1.4, 1],
            gap="large",
            vertical_alignment="top",
        )
    )

    with activity_column:

        with dashboard_widget(
            title="Latest activity",
            icon=":material/history:",
            divider=True,
        ):

            if (
                today.latest_activity_summary
                is None
            ):

                _show_empty_state(
                    title="No recent activity",
                    message=(
                        "Import an activity to compare "
                        "completed and planned training."
                    ),
                )

            else:

                activity_outcome = (
                    _activity_outcome_summary(
                        today.latest_activity_summary
                    )
                )

                st.markdown(
                    f"**Plan result:** {activity_outcome}"
                )

                latest_activity_card(
                    today.latest_activity
                )

    with event_column:

        with dashboard_widget(
            title="Next event",
            icon=":material/event:",
            divider=True,
        ):

            if today.next_event is None:

                _show_empty_state(
                    title="No upcoming event",
                    message=(
                        "Add an event to give the "
                        "training plan a target."
                    ),
                )

            else:

                next_event_card(
                    today.next_event
                )

    return None