"""
PerformanceLab

Athlete settings page.
"""

import streamlit as st

from .athlete_panel import (
    show_athlete_panel,
)


def show_settings_page(
    athlete,
):
    """
    Displays athlete settings while reusing the
    existing validated athlete editor.
    """

    st.title(
        "Settings"
    )

    st.caption(
        "Manage the personal, physiological, nutrition "
        "and availability information used by "
        "PerformanceLab."
    )

    st.info(
        "Changes to physiological values, heart-rate "
        "zones and availability can influence future "
        "training plans and recommendations."
    )

    st.divider()

    st.subheader(
        "Athlete profile"
    )

    st.caption(
        "These values are inputs to the PerformanceLab "
        "domain and planning system."
    )

    return show_athlete_panel(
        athlete,
        show_heading=False,
    )