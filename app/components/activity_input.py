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


def show_activity_input(
    athlete,
    *,
    key_prefix: str = "activity",
    show_header: bool = True,
):
    """
    Displays controls for adding an activity manually
    or importing it from a supported file.

    Returns
    -------
    Athlete
        Current athlete instance.
    """

    if show_header:

        st.header(
            "Add activity"
        )

    mode = st.segmented_control(
        "Activity source",
        options=[
            "Manual",
            "File",
        ],
        default="File",
        label_visibility="collapsed",
        key=f"{key_prefix}_input_mode",
    )

    if mode == "Manual":

        show_manual_workout_form(
            athlete,
            key_prefix=key_prefix,
        )

    elif mode == "File":

        show_import_panel(
            athlete,
            key_prefix=key_prefix,
        )

    return athlete