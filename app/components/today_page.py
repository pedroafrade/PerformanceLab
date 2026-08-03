"""
PerformanceLab

Today page.
"""

import streamlit as st


def show_today_page(
    athlete,
):
    """
    Displays the athlete's daily decision page.

    This page is independent from the main dashboard.
    """

    st.title(
        "Today"
    )

    st.caption(
        "Your current training context and the decisions "
        "that matter today."
    )

    st.info(
        "The Today page is ready for its dedicated "
        "daily training content."
    )

    return None