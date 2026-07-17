"""
PerformanceLab

Activity Input Component.
"""

import streamlit as st

from ._manual_workout_form import (
    show_manual_workout_form,
)
from .import_panel import (
    show_import_panel,
)


# ======================================================
# Activity input
# ======================================================

def show_activity_input(
    athlete,
):

    """
    Displays controls for adding an activity manually
    or importing it from a supported file.

    Returns
    -------
    Athlete
        Current athlete instance.
    """

    st.header("Add activity")

    mode = st.segmented_control(
        "Activity source",
        options=[
            "Manual",
            "File",
        ],
        default="File",
        label_visibility="collapsed",
        key="activity_input_mode",
    )

    if mode == "Manual":

        show_manual_workout_form(
            athlete
        )

    elif mode == "File":

        show_import_panel(
            athlete
        )

    return athlete