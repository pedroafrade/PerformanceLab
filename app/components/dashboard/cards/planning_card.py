"""
PerformanceLab

Planning dashboard card.
"""

import streamlit as st


def show_planning_card(
    planning,
) -> None:
    """
    Displays the planning card.
    """

    st.divider()

    st.subheader(
        "Planning"
    )

    column_1, column_2 = st.columns(2)

    next_goal = planning["next_goal"]

    with column_1:

        st.markdown(
            "#### Next goal"
        )

        if next_goal is None:

            st.write(
                "No active goals."
            )

        else:

            st.write(
                next_goal.name
                or "Unnamed goal"
            )

            st.write(
                f"{planning['days_until_next_goal']} "
                "days remaining"
            )

    next_event = planning["next_event"]

    with column_2:

        st.markdown(
            "#### Next event"
        )

        if next_event is None:

            st.write(
                "No upcoming events."
            )

        else:

            st.write(
                next_event.event.name
                or "Unnamed event"
            )

            st.write(
                f"{planning['days_until_next_event']} "
                "days remaining"
            )