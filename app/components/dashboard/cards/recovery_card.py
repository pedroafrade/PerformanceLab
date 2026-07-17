"""
Recovery dashboard card.
"""

from __future__ import annotations

import streamlit as st

from performancelab.presentation.dashboard_models import RecoveryCardData


def recovery_card(data: RecoveryCardData) -> None:
    """
    Render the recovery dashboard card.
    """

    score_col, trend_col = st.columns([3, 1], vertical_alignment="center")

    with score_col:
        st.markdown(
            (
                "<div style='"
                "font-size:2.75rem;"
                "font-weight:700;"
                "line-height:1;"
                "margin-bottom:0.25rem;'>"
                f"{data.score}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    with trend_col:
        if data.trend:
            st.metric(
                label="Trend",
                value=data.trend,
            )

    st.caption(data.status)

    st.info(data.recommendation)