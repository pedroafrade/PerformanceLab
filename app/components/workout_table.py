"""
PerformanceLab

Workout Table Component.
"""

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st


# ======================================================
# Formatting
# ======================================================

def format_workout_date(value) -> str:

    if value is None:

        return "—"

    if isinstance(value, datetime):

        return value.strftime(
            "%Y-%m-%d %H:%M"
        )

    return value.strftime(
        "%Y-%m-%d"
    )


# ======================================================

def format_duration(
    value: timedelta | None,
) -> str:

    if value is None:

        return "—"

    total_seconds = int(
        value.total_seconds()
    )

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes = remainder // 60

    return f"{hours}h {minutes:02d}m"


# ======================================================

def format_distance(
    value: float | None,
) -> str:

    if value is None:

        return "—"

    return f"{value:.2f} km"


# ======================================================

def format_elevation(
    value: float | None,
) -> str:

    if value is None:

        return "—"

    return f"{value:.0f} m"

# ======================================================

def get_selected_workouts(
    athlete,
    *,
    key: str = "workout_history_table",
) -> list:
    """
    Return all workouts selected in the dataframe.
    """

    workouts = list(
        reversed(
            athlete.history.workouts
        )
    )

    if not workouts:
        return []

    selection_state = st.session_state.get(
        key
    )

    if selection_state is None:
        return []

    try:
        selected_rows = (
            selection_state.selection.rows
        )
    except AttributeError:
        selection = selection_state.get(
            "selection",
            {},
        )

        try:
            selected_rows = selection.rows
        except AttributeError:
            selected_rows = selection.get(
                "rows",
                [],
            )

    return [
        workouts[index]
        for index in selected_rows
        if index < len(workouts)
    ]


# ======================================================

def get_selected_workout(
    athlete,
    *,
    key: str = "workout_history_table",
):
    """
    Return the single selected workout.
    """

    selected_workouts = (
        get_selected_workouts(
            athlete,
            key=key,
        )
    )

    if len(selected_workouts) != 1:
        return None

    return selected_workouts[0]

# ======================================================
# Workout table
# ======================================================

def show_workout_table(
    athlete,
    *,
    key: str = "workout_history_table",
    show_header: bool = True,
    selection_mode: str = "single-row",
):

    if show_header:

        st.divider()

        st.subheader(
            "Workout history"
        )

    workouts = list(

        reversed(
            athlete.history.workouts
        )

    )

    if not workouts:

        st.info(
            "No workouts available."
        )

        return None

    rows = [

        {
            "Date": format_workout_date(
                workout.date
            ),

            "Title": (
                workout.info.title
                or "—"
            ),

            "Sport": (
                workout.sport
                or "Unknown"
            ),

            "Distance": format_distance(
                workout.distance
            ),

            "Duration": format_duration(
                workout.duration
            ),

            "Elevation": format_elevation(
                workout.elevation_gain
            ),

            "RPE": workout.feedback.effective_rpe,

            "Source": (
                workout.info.source
                or "—"
            ),

        }

        for workout in workouts

    ]

    table = pd.DataFrame(rows)

    selection_event = st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        key=key,
        on_select="rerun",
        selection_mode=selection_mode,
    )

    selected_rows = (
        selection_event.selection.rows
    )

    if not selected_rows:

        st.caption(
            "Select a workout in the table "
            "to view its details."
        )

        return None

    selected_workouts = [
        workouts[index]
        for index in selected_rows
        if index < len(workouts)
    ]

    if selection_mode == "multi-row":

        return selected_workouts

    if not selected_workouts:

        return None

    return selected_workouts[0]