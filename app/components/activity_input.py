"""
PerformanceLab

Activity Input Component.
"""

import streamlit as st

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
    Displays activity input controls.

    Returns
    -------
    Athlete
        Athlete instance.
    """

    st.header(

        "Activity"

    )

    mode = st.segmented_control(

        "Source",

        options=[

            "Manual",

            "File",

        ],

        default="File",

        label_visibility="collapsed",

    )

    if mode == "File":

        show_import_panel(

            athlete,

        )

    else:

        st.info(

            "Manual workout form "
            "coming soon."

        )

    return athlete