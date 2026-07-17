"""
PerformanceLab

Performance management dashboard card.
"""

import streamlit as st


def show_performance_management_card(
    summary,
) -> None:
    """
    Displays the performance management card.
    """

    st.divider()

    st.subheader(
        "Performance management"
    )

    (
        column_1,
        column_2,
        column_3,
    ) = st.columns(3)

    column_1.metric(
        "CTL — Fitness",
        f"{summary['ctl']:.1f}",
    )

    column_2.metric(
        "ATL — Fatigue",
        f"{summary['atl']:.1f}",
    )

    column_3.metric(
        "TSB — Form",
        f"{summary['tsb']:.1f}",
    )