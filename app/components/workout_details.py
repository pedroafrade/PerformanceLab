"""
PerformanceLab

Workout Details Component.
"""

from datetime import timedelta

import streamlit as st

from performancelab.presentation import (
    cadence_card,
    heart_rate_card,
    power_card,
)

from .sensor_card import show_sensor_card


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

    column_1, \
        column_2, \
        column_3, \
        column_4 = st.columns(4)

    column_1.metric(
        "Distance",
        format_distance(
            workout.distance
        ),
    )

    column_2.metric(
        "Duration",
        format_duration(
            workout.duration
        ),
    )

    column_3.metric(
        "Elevation",
        format_elevation(
            workout.elevation_gain
        ),
    )

    column_4.metric(
        "RPE",
        (
            f"{workout.feedback.rpe:.1f}"
            if workout.feedback.rpe is not None
            else "—"
        ),
    )


# ======================================================
# Sensor analysis
# ======================================================

def show_workout_sensors(
    workout,
) -> None:

    show_sensor_card(
        heart_rate_card(workout)
    )

    show_sensor_card(
        power_card(workout)
    )

    show_sensor_card(
        cadence_card(workout)
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

    show_workout_sensors(
        workout
    )
    