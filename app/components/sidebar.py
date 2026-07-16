"""
PerformanceLab

Sidebar Component.
"""

import streamlit as st

from .activity_input import (
    show_activity_input,
)
from .athlete_panel import (
    show_athlete_panel,
)
from .storage_panel import (
    show_storage_panel,
)


# ======================================================
# Sidebar
# ======================================================

def show_sidebar(
    athlete,
):

    """
    Displays the application sidebar.

    Returns
    -------
    Athlete
        Current athlete instance.
    """

    with st.sidebar:

        st.title("PerformanceLab")

        athlete = show_storage_panel(
            athlete
        )

        st.divider()

        athlete = show_athlete_panel(
            athlete
        )

        st.divider()

        athlete = show_activity_input(
            athlete
        )

    return athlete