"""Compact Dashboard view of the shared upcoming-event component."""

import streamlit as st

from ...upcoming_events import (
    upcoming_events_html,
    upcoming_events_styles,
)


def next_event_card(event) -> None:
    """Display the nearest event using the shared event renderer."""

    st.markdown(
        "<style>" + upcoming_events_styles() + "</style>"
        + upcoming_events_html((event,), compact=True),
        unsafe_allow_html=True,
    )
