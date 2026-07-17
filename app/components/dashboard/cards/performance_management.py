"""
PerformanceLab

Performance management dashboard card.
"""

import streamlit as st


def show_performance_management_card(
    summary,
) -> None:
    """
    Displays the current performance status.
    """

    column_1, column_2, column_3 = st.columns(3)

    column_1.metric(
        "Fitness",
        f"{summary.ctl:.1f}",
    )

    column_2.metric(
        "Fatigue",
        f"{summary.atl:.1f}",
    )

    column_3.metric(
        "Form",
        f"{summary.tsb:.1f}",
    )

    if summary.tsb >= 10:

        st.success(
            "Fresh and ready."
        )

    elif summary.tsb >= -10:

        st.info(
            "Balanced training state."
        )

    else:

        st.warning(
            "High fatigue. Recovery may be needed."
        )