"""
PerformanceLab

Workout Details Component.
"""

from datetime import timedelta

import streamlit as st


# ======================================================
# Formatting
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
# Workout summary
# ======================================================

def show_workout_summary(
    workout,
) -> None:

    detail_column_1, \
        detail_column_2, \
        detail_column_3, \
        detail_column_4 = st.columns(4)

    detail_column_1.metric(

        "Distance",

        format_distance(
            workout.distance
        ),

    )

    detail_column_2.metric(

        "Duration",

        format_duration(
            workout.duration
        ),

    )

    detail_column_3.metric(

        "Elevation",

        format_elevation(
            workout.elevation_gain
        ),

    )

    detail_column_4.metric(

        "RPE",

        (
            f"{workout.feedback.rpe:.1f}"
            if workout.feedback.rpe is not None
            else "—"
        ),

    )


# ======================================================
# Workout details
# ======================================================

def show_workout_details(
    workout,
) -> None:

    show_workout_summary(
        workout
    )