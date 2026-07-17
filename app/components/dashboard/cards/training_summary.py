"""
PerformanceLab

Training summary dashboard card.
"""

import streamlit as st

from .common import format_duration


def show_training_summary_card(
    summary,
) -> None:
    """
    Displays the weekly training summary.
    """

    st.markdown("##### This Week")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "🏃 Workouts",
            summary.workouts,
        )

        st.metric(
            "⏱ Duration",
            format_duration(
                summary.total_duration
            ),
        )

    with col2:

        st.metric(
            "🗓 Training days",
            summary.training_days,
        )

        st.metric(
            "🚴 Sports",
            summary.sports,
        )