"""
PerformanceLab

Planning dashboard card.
"""

import streamlit as st


def show_planning_card(
    planning,
) -> None:
    """
    Displays the athlete planning information.
    """

    st.markdown("##### Planning")

    goal_column, event_column = st.columns(2)

    with goal_column:

        st.markdown("**Next goal**")

        if planning.next_goal is None:

            st.caption(
                "No goal defined."
            )

        else:

            st.write(
                planning.next_goal
            )

            if planning.days_to_goal is not None:

                st.caption(
                    f"{planning.days_to_goal} days remaining"
                )

    with event_column:

        st.markdown("**Next event**")

        if planning.next_event is None:

            st.caption(
                "No event scheduled."
            )

        else:

            st.write(
                planning.next_event
            )

            if planning.days_to_event is not None:

                st.caption(
                    f"{planning.days_to_event} days remaining"
                )