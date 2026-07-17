"""
PerformanceLab

Training summary dashboard card.
"""

import streamlit as st

from .common import (
    format_duration,
)


def show_training_summary_card(
    summary,
) -> None:
    """
    Displays the training summary card.
    """

    st.divider()

    st.subheader(
        "Training summary"
    )

    (
        column_1,
        column_2,
        column_3,
        column_4,
    ) = st.columns(4)

    column_1.metric(
        "Workouts",
        summary["workouts"],
    )

    column_2.metric(
        "Training days",
        summary["training_days"],
    )

    column_3.metric(
        "Total duration",
        format_duration(
            summary["total_duration"]
        ),
    )

    average_rpe = summary["average_rpe"]

    column_4.metric(
        "Average RPE",
        (
            f"{average_rpe:.1f}"
            if average_rpe is not None
            else "—"
        ),
    )