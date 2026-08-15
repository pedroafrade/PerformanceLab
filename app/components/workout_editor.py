"""
PerformanceLab

Workout actions and editor component.
"""

from datetime import (
    datetime,
    timedelta,
)

import streamlit as st

from performancelab.application import (
    WorkoutUpdate,
)


def _initialize_workout_editor_state() -> None:
    """
    Initialize session-state values used by the editor.
    """

    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False

    if "edit_workout" not in st.session_state:
        st.session_state.edit_workout = False


def show_workout_edit_action(
    selected_workout,
    *,
    key: str = "edit_workout_action",
) -> None:
    """
    Display the Edit action.
    """

    _initialize_workout_editor_state()

    if selected_workout is None:
        return

    if st.button(
        "Edit",
        key=key,
        use_container_width=True,
    ):

        st.session_state.confirm_delete = False
        st.session_state.edit_workout = True
        st.rerun()


def show_workout_delete_action(
    selected_workout,
    *,
    on_delete_workouts=None,
    key_prefix: str = "delete_workout_action",
) -> None:
    """
    Display deletion for one or multiple workouts.
    """

    _initialize_workout_editor_state()

    if selected_workout is None:
        return

    if isinstance(
        selected_workout,
        (
            list,
            tuple,
        ),
    ):

        selected_workouts = list(
            selected_workout
        )

    else:

        selected_workouts = [
            selected_workout
        ]

    if not selected_workouts:
        return

    workout_count = len(
        selected_workouts
    )

    if st.button(
        "Delete",
        key=f"{key_prefix}_open",
        use_container_width=True,
        disabled=(
            on_delete_workouts
            is None
        ),
    ):

        st.session_state.edit_workout = False
        st.session_state.confirm_delete = True

    if not st.session_state.confirm_delete:
        return

    modal_key = (
        f"{key_prefix}_modal"
    )

    st.markdown(
        f"""
        <style>
        .workout-delete-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.25);
            z-index: 999;
        }}

        .st-key-{modal_key} {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: min(500px, calc(100vw - 2rem));
            padding: 1.25rem;
            background: white;
            border: 1px solid #d9d9d9;
            border-radius: 0.75rem;
            box-shadow:
                0 1rem 3rem rgba(0, 0, 0, 0.25);
            z-index: 1000;
        }}
        </style>

        <div class="workout-delete-backdrop"></div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(
        key=modal_key,
        border=True,
    ):

        if workout_count == 1:

            st.subheader(
                "Delete workout"
            )

            st.warning(
                "Are you sure you want to "
                "delete this workout?"
            )

        else:

            st.subheader(
                f"Delete {workout_count} workouts"
            )

            st.warning(
                "Are you sure you want to "
                f"delete these {workout_count} "
                "workouts?"
            )

        confirm_column, cancel_column = (
            st.columns(2)
        )

        with confirm_column:

            if st.button(
                "Delete",
                key=f"{key_prefix}_confirm",
                type="primary",
                use_container_width=True,
            ):

                workout_ids = tuple(
                    workout.workout_id
                    for workout
                    in selected_workouts
                )

                try:

                    result = on_delete_workouts(
                        workout_ids
                    )

                except Exception:

                    st.error(
                        "The workout could not be deleted."
                    )

                    return

                st.session_state.confirm_delete = False
                st.session_state.edit_workout = False

                if result.removed_count == 1:

                    message = (
                        "Workout deleted."
                    )

                else:

                    message = (
                        f"{result.removed_count} "
                        "workouts deleted."
                    )

                st.session_state.persisted_notice = (
                    message
                )

                st.rerun()

        with cancel_column:

            if st.button(
                "Cancel",
                key=f"{key_prefix}_cancel",
                use_container_width=True,
            ):

                st.session_state.confirm_delete = False
                st.rerun()


def _updated_workout_date(
    selected_workout,
    workout_date,
):
    """
    Preserve the factual start time when changing the day.
    """

    original_date = (
        selected_workout.info.date
    )

    if isinstance(
        original_date,
        datetime,
    ):

        return datetime.combine(
            workout_date,
            original_date.timetz(),
        )

    return workout_date


def _show_workout_edit_fields(
    selected_workout,
    *,
    on_update_workout,
    key_prefix: str,
) -> None:
    """
    Display editable workout fields inside the modal.
    """

    title = st.text_input(
        "Title",
        value=(
            selected_workout.info.title
            or ""
        ),
        key=f"{key_prefix}_title",
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
        index=(
            sports.index(
                current_sport
            )
        ),
        key=f"{key_prefix}_sport",
    )

    workout_date = st.date_input(
        "Date",
        value=selected_workout.date,
        key=f"{key_prefix}_date",
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        value=float(
            selected_workout.distance
            or 0
        ),
        step=0.1,
        key=f"{key_prefix}_distance",
    )

    duration = (
        selected_workout.duration
        if selected_workout.duration
        is not None
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
        hours_column,
        minutes_column,
        seconds_column,
    ) = st.columns(3)

    with hours_column:

        hours = st.number_input(
            "Hours",
            min_value=0,
            value=initial_hours,
            step=1,
            key=f"{key_prefix}_hours",
        )

    with minutes_column:

        minutes = st.number_input(
            "Minutes",
            min_value=0,
            max_value=59,
            value=initial_minutes,
            step=1,
            key=f"{key_prefix}_minutes",
        )

    with seconds_column:

        seconds = st.number_input(
            "Seconds",
            min_value=0,
            max_value=59,
            value=initial_seconds,
            step=1,
            key=f"{key_prefix}_seconds",
        )

    elevation = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        value=float(
            selected_workout.elevation_gain
            or 0
        ),
        step=1.0,
        key=f"{key_prefix}_elevation",
    )

    estimated_rpe = getattr(
        selected_workout.feedback,
        "estimated_rpe",
        None,
    )

    manual_rpe = (
        selected_workout.feedback.rpe
    )

    effective_rpe = getattr(
        selected_workout.feedback,
        "effective_rpe",
        manual_rpe
        or estimated_rpe,
    )

    if estimated_rpe is not None:

        st.info(
            "Automatic RPE estimate: "
            f"{estimated_rpe:.1f}"
        )

    use_manual_rpe = st.checkbox(
        "Set RPE manually",
        value=(
            manual_rpe is not None
            or estimated_rpe is None
        ),
        key=f"{key_prefix}_manual_rpe",
    )

    rpe = st.slider(
        "RPE",
        min_value=1,
        max_value=10,
        value=int(
            round(
                effective_rpe
                or 5
            )
        ),
        disabled=(
            not use_manual_rpe
        ),
        key=f"{key_prefix}_rpe",
    )

    save_column, cancel_column = (
        st.columns(2)
    )

    with save_column:

        if st.button(
            "Save",
            key=f"{key_prefix}_save",
            type="primary",
            use_container_width=True,
        ):

            update = WorkoutUpdate(
                title=title,
                sport=sport,
                workout_date=(
                    _updated_workout_date(
                        selected_workout,
                        workout_date,
                    )
                ),
                distance=(
                    distance
                    if distance > 0
                    else None
                ),
                duration=timedelta(
                    hours=int(
                        hours
                    ),
                    minutes=int(
                        minutes
                    ),
                    seconds=int(
                        seconds
                    ),
                ),
                elevation_gain=elevation,
                rpe=(
                    float(
                        rpe
                    )
                    if use_manual_rpe
                    else None
                ),
            )

            try:

                result = on_update_workout(
                    selected_workout.workout_id,
                    update,
                )

            except Exception:

                st.error(
                    "The workout could not be updated."
                )

                return

            st.session_state.edit_workout = False

            if result.changed:

                st.session_state.persisted_notice = (
                    "Workout updated."
                )

            else:

                st.session_state.persisted_notice = (
                    "No workout changes were required."
                )

            st.rerun()

    with cancel_column:

        if st.button(
            "Cancel",
            key=f"{key_prefix}_cancel",
            use_container_width=True,
        ):

            st.session_state.edit_workout = False
            st.rerun()


def show_workout_edit_form(
    selected_workout,
    *,
    on_update_workout=None,
    key_prefix: str = "workout_edit_form",
) -> None:
    """
    Open the workout editor in a modal.
    """

    _initialize_workout_editor_state()

    if (
        selected_workout is None
        or not st.session_state.edit_workout
        or on_update_workout is None
    ):
        return

    def show_dialog_content() -> None:

        _show_workout_edit_fields(
            selected_workout,
            on_update_workout=(
                on_update_workout
            ),
            key_prefix=key_prefix,
        )

    edit_dialog = st.dialog(
        "Edit workout",
        width="large",
    )(
        show_dialog_content
    )

    edit_dialog()


def show_workout_editor(
    selected_workout,
    *,
    on_update_workout=None,
    on_delete_workouts=None,
    key_prefix: str = "workout_editor",
) -> None:
    """
    Display workout actions and the edit form.
    """

    _initialize_workout_editor_state()

    if selected_workout is None:

        st.session_state.confirm_delete = False
        st.session_state.edit_workout = False

        return

    edit_column, delete_column = (
        st.columns(
            2,
            gap="small",
        )
    )

    with edit_column:

        show_workout_edit_action(
            selected_workout,
            key=f"{key_prefix}_edit",
        )

    with delete_column:

        show_workout_delete_action(
            selected_workout,
            on_delete_workouts=(
                on_delete_workouts
            ),
            key_prefix=(
                f"{key_prefix}_delete"
            ),
        )

    show_workout_edit_form(
        selected_workout,
        on_update_workout=(
            on_update_workout
        ),
        key_prefix=(
            f"{key_prefix}_form"
        ),
    )