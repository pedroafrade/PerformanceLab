"""
PerformanceLab

Workout actions and editor component.
"""

from datetime import timedelta

import streamlit as st


# ======================================================
# Session state
# ======================================================

def _initialize_workout_editor_state() -> None:

    """
    Initializes the session-state values used by the
    workout editor.
    """

    if "confirm_delete" not in st.session_state:

        st.session_state.confirm_delete = False

    if "edit_workout" not in st.session_state:

        st.session_state.edit_workout = False


# ======================================================
# Workout actions
# ======================================================

def _show_workout_actions(
    athlete,
    selected_workout,
) -> None:

    """
    Displays the edit and delete actions for the selected
    workout.
    """

    st.divider()

    if not st.session_state.confirm_delete:

        action_column_1, action_column_2 = st.columns(2)

        with action_column_1:

            if st.button(
                "🗑 Delete workout",
                use_container_width=True,
            ):

                st.session_state.confirm_delete = True

                st.rerun()

        with action_column_2:

            if st.button(
                "✏️ Edit workout",
                use_container_width=True,
            ):

                st.session_state.edit_workout = True

                st.rerun()

        return

    st.warning(
        "Are you sure you want to delete this workout?"
    )

    confirm_column, cancel_column = st.columns(2)

    with confirm_column:

        if st.button(
            "✅ Delete",
            type="primary",
            use_container_width=True,
        ):

            athlete.history.remove(
                selected_workout
            )

            st.session_state.confirm_delete = False
            st.session_state.edit_workout = False

            st.session_state.notice = (
                "Workout deleted."
            )

            st.rerun()

    with cancel_column:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.confirm_delete = False

            st.rerun()


# ======================================================
# Workout edit form
# ======================================================

def _show_workout_edit_form(
    athlete,
    selected_workout,
) -> None:

    """
    Displays the form used to edit the selected workout.
    """

    if not st.session_state.edit_workout:

        return

    st.divider()

    st.subheader(
        "Edit workout"
    )

    title = st.text_input(
        "Title",
        value=selected_workout.info.title or "",
    )

    sports = [
        "Running",
        "Cycling",
        "Swimming",
        "Walking",
        "Hiking",
        "Strength",
        "Other",
    ]

    current_sport = (
        selected_workout.sport
        if selected_workout.sport in sports
        else "Other"
    )

    sport = st.selectbox(
        "Sport",
        sports,
        index=sports.index(
            current_sport
        ),
    )

    workout_date = st.date_input(
        "Date",
        value=selected_workout.date,
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        value=float(
            selected_workout.distance or 0
        ),
        step=0.1,
    )

    duration = (
        selected_workout.duration
        if selected_workout.duration is not None
        else timedelta()
    )

    total_seconds = int(
        duration.total_seconds()
    )

    initial_hours = (
        total_seconds // 3600
    )

    initial_minutes = (
        total_seconds % 3600
    ) // 60

    initial_seconds = (
        total_seconds % 60
    )

    (
        duration_column_1,
        duration_column_2,
        duration_column_3,
    ) = st.columns(3)

    with duration_column_1:

        hours = st.number_input(
            "Hours",
            min_value=0,
            value=initial_hours,
            step=1,
        )

    with duration_column_2:

        minutes = st.number_input(
            "Minutes",
            min_value=0,
            max_value=59,
            value=initial_minutes,
            step=1,
        )

    with duration_column_3:

        seconds = st.number_input(
            "Seconds",
            min_value=0,
            max_value=59,
            value=initial_seconds,
            step=1,
        )

    elevation = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        value=float(
            selected_workout.elevation_gain or 0
        ),
        step=1.0,
    )

    rpe = st.slider(
        "RPE",
        min_value=1,
        max_value=10,
        value=int(
            selected_workout.feedback.rpe or 5
        ),
    )

    save_column, cancel_column = st.columns(2)

    with save_column:

        if st.button(
            "💾 Save",
            type="primary",
            use_container_width=True,
        ):

            selected_workout.info.title = title
            selected_workout.info.sport = sport
            selected_workout.info.date = workout_date

            selected_workout.info.distance = (
                distance
                if distance > 0
                else None
            )

            selected_workout.info.duration = timedelta(
                hours=int(hours),
                minutes=int(minutes),
                seconds=int(seconds),
            )

            selected_workout.info.elevation_gain = (
                elevation
            )

            selected_workout.feedback.rpe = rpe

            athlete.history._sort()

            st.session_state.edit_workout = False

            st.session_state.notice = (
                "Workout updated."
            )

            st.rerun()

    with cancel_column:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            st.session_state.edit_workout = False

            st.rerun()


# ======================================================
# Public component
# ======================================================

def show_workout_editor(
    athlete,
    selected_workout,
) -> None:

    """
    Displays the actions and editor for the selected
    workout.

    Parameters
    ----------
    athlete
        Athlete that owns the selected workout.

    selected_workout
        Workout currently selected in the dashboard.
    """

    _initialize_workout_editor_state()

    if selected_workout is None:

        st.session_state.confirm_delete = False
        st.session_state.edit_workout = False

        return

    _show_workout_actions(
        athlete,
        selected_workout,
    )

    _show_workout_edit_form(
        athlete,
        selected_workout,
    )