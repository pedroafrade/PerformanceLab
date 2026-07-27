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
    get_selected_workout,
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

    selected_workout = get_selected_workout(
        athlete,
        key=table_key,
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

        with delete_column:
            show_workout_delete_action(
                athlete,
                selected_workout,
                key_prefix="training_delete_workout",
            )

    selected_workout = show_workout_table(
        athlete,
        key=table_key,
        show_header=False,
    )

    if selected_workout is None:
        return None

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