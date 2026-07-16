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
# Workout label
# ======================================================

def workout_label(workout) -> str:

    return (

        f"{format_workout_date(workout.date)} — "

        f"{workout.sport or 'Unknown'} — "

        f"{workout.info.title or 'Untitled'} — "

        f"{workout.info.source or 'unknown'}"

    )


# ======================================================
# Workout table
# ======================================================

def show_workout_table(
    athlete,
):

    st.divider()

    st.subheader("Workout history")

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

            "RPE": workout.feedback.rpe,

            "Source": (
                workout.info.source
                or "—"
            ),

        }

        for workout in workouts

    ]

    table = pd.DataFrame(rows)

    st.dataframe(

        table,

        width="stretch",

        hide_index=True,

    )

    st.subheader("Workout details")

    selected_index = st.selectbox(

        "Select workout",

        options=range(len(workouts)),

        format_func=lambda index: (
            workout_label(
                workouts[index]
            )
        ),

    )

    return workouts[selected_index]