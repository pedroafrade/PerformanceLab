"""
PerformanceLab

Training page.
"""

import streamlit as st

from .workout_details import (
    show_workout_details,
)
from .workout_editor import (
    show_workout_delete_action,
    show_workout_edit_action,
    show_workout_edit_form,
)
from .workout_table import (
    get_selected_workouts,
    show_workout_table,
)


# ======================================================
# Training page
# ======================================================

def show_training_page(
    athlete,
):
    """
    Display training history and workout actions.

    Parameters
    ----------
    athlete
        Athlete whose workouts are displayed.

    Returns
    -------
    Workout | None
        Workout selected in the history table.
    """

    st.title("Training")

    # --------------------------------------------------
    # Workout history
    # --------------------------------------------------

    table_key = "training_workout_history_table"

    selected_workouts = (
        get_selected_workouts(
            athlete,
            key=table_key,
        )
    )

    selected_workout = (
        selected_workouts[0]
        if len(selected_workouts) == 1
        else None
    )

    st.divider()

    (
        history_column,
        edit_column,
        delete_column,
    ) = st.columns([8, 1, 1])

    with history_column:
        st.subheader("Workout history")

    if selected_workout is not None:

        with edit_column:
            show_workout_edit_action(
                selected_workout,
                key="training_edit_workout",
            )

    if selected_workouts:

        with delete_column:
            show_workout_delete_action(
                athlete,
                selected_workouts,
                key_prefix="training_delete_workout",
            )

    selected_workouts = (
        show_workout_table(
            athlete,
            key=table_key,
            show_header=False,
            selection_mode="multi-row",
        )
        or []
    )

    if not selected_workouts:
        return None

    if len(selected_workouts) > 1:

        st.caption(
            f"{len(selected_workouts)} "
            "workouts selected."
        )

        return None

    selected_workout = (
        selected_workouts[0]
    )

    # --------------------------------------------------
    # Workout details
    # --------------------------------------------------

    show_workout_details(
        selected_workout,
    )

    # --------------------------------------------------
    # Workout edit form
    # --------------------------------------------------

    show_workout_edit_form(
        athlete,
        selected_workout,
        key_prefix="training_workout_edit_form",
    )

    return selected_workout