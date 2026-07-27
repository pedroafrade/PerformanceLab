"""
PerformanceLab

Training page.
"""

import streamlit as st

from .import_panel import (
    show_import_panel,
)
from .workout_details import (
    show_workout_details,
)
from .workout_editor import (
    show_workout_editor,
)
from .workout_table import (
    show_workout_table,
)


# ======================================================
# Training page
# ======================================================

def show_training_page(
    athlete,
):
    """
    Display the athlete training history and workout actions.

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
    # Import activity
    # --------------------------------------------------

    st.subheader("Import activity")

    show_import_panel(
        athlete,
        key_prefix="training_page",
    )

    # --------------------------------------------------
    # Workout history
    # --------------------------------------------------

    selected_workout = show_workout_table(
        athlete
    )

    if selected_workout is None:

        return None

    # --------------------------------------------------
    # Workout details
    # --------------------------------------------------

    show_workout_details(
        selected_workout
    )

    # --------------------------------------------------
    # Edit and delete actions
    # --------------------------------------------------

    show_workout_editor(
        athlete,
        selected_workout,
    )

    return selected_workout