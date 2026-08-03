"""
PerformanceLab

Activities page.
"""

from datetime import timedelta

import streamlit as st

from performancelab.presentation import (
    ActivitiesPresenter,
)

from .workout_table import (
    format_distance,
    format_duration,
    format_elevation,
    format_workout_date,
)


def _activity_rows(
    activities,
) -> list[dict]:
    """
    Converts activity presentation data into table rows.
    """

    return [
        {
            "Date": format_workout_date(
                activity.workout_date
            ),
            "Activity": activity.title,
            "Sport": activity.sport,
            "Distance": format_distance(
                activity.distance
            ),
            "Duration": format_duration(
                activity.duration
            ),
            "Elevation": format_elevation(
                activity.elevation_gain
            ),
            "RPE": (
                activity.rpe
                if activity.rpe is not None
                else "—"
            ),
        }
        for activity in activities
    ]


def _total_duration(
    activities,
) -> timedelta:
    """
    Returns the accumulated duration of the activities.
    """

    return sum(
        (
            activity.duration
            or timedelta()
            for activity in activities
        ),
        timedelta(),
    )


def show_activities_page(
    athlete,
) -> None:
    """
    Displays the athlete's completed activity history.
    """

    st.title("Activities")

    st.caption(
        "Review completed training and imported activity data."
    )

    activities = ActivitiesPresenter(
        athlete.history
    ).build()

    if not activities:

        st.info(
            "No activities are available yet. "
            "Import a file or add an activity manually."
        )

        return

    total_duration = _total_duration(
        activities
    )

    sports = {
        activity.sport
        for activity in activities
    }

    activity_column, sport_column, duration_column = (
        st.columns(3)
    )

    with activity_column:

        st.metric(
            "Activities",
            len(activities),
        )

    with sport_column:

        st.metric(
            "Sports",
            len(sports),
        )

    with duration_column:

        st.metric(
            "Total duration",
            format_duration(
                total_duration
            ),
        )

    st.divider()

    st.subheader(
        "Activity history"
    )

    st.dataframe(
        _activity_rows(
            activities
        ),
        width="stretch",
        hide_index=True,
    )