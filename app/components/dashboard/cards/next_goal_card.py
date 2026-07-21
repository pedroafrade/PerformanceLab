"""
PerformanceLab

Next Goal Card
"""

import streamlit as st


def next_goal_card(goal):

    """
    Displays the next goal.
    """

    if goal is None or goal.name is None:

        st.info(
            "No active goals."
        )

        return

    st.markdown(
        f"### {goal.name}"
    )

    if goal.description:

        st.caption(
            goal.description
        )

    left, right = st.columns(2)

    with left:

        st.metric(
            "Target",
            goal.target_date.strftime("%d %b %Y"),
        )

    with right:

        if goal.days_remaining == 0:

            value = "Today"

        elif goal.days_remaining == 1:

            value = "Tomorrow"

        else:

            value = f"{goal.days_remaining} days"

        st.metric(
            "Remaining",
            value,
        )

    if goal.priority:

        st.caption(
            f"Priority: {goal.priority}"
        )