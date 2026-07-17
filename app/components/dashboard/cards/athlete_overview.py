"""
PerformanceLab

Athlete overview dashboard card.
"""

import streamlit as st


def show_athlete_overview_card(
    dashboard_data,
) -> None:
    """
    Displays the athlete overview card.
    """

    if st.session_state.notice:

        st.success(
            st.session_state.notice
        )

        st.session_state.notice = None

    athlete = dashboard_data["athlete"]

    st.subheader(
        athlete["name"]
        or "Unnamed athlete"
    )

    sports = athlete["sports"]

    if sports:

        st.write(
            "**Sports:**",
            ", ".join(sports),
        )

    else:

        st.write(
            "**Sports:** —"
        )