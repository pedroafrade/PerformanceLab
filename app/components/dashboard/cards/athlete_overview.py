"""
PerformanceLab

Athlete overview dashboard card.
"""

import streamlit as st


def show_athlete_overview_card(
    dashboard_data,
) -> None:
    """
    Displays dashboard notifications.
    """

    del dashboard_data

    notice = st.session_state.get(
        "notice"
    )

    if notice:

        st.success(
            notice
        )

        st.session_state.notice = None