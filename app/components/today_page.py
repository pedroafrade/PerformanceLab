"""
PerformanceLab

Today page.
"""

import streamlit as st

from .dashboard import (
    show_dashboard,
)


def show_today_page(
    athlete,
):
    """
    Displays the athlete's current-day overview.

    The existing dashboard remains intact and is
    composed inside the Today page.
    """

    st.title(
        "Today"
    )

    st.caption(
        "Your current training context, next decisions "
        "and most relevant athlete information."
    )

    return show_dashboard(
        athlete
    )