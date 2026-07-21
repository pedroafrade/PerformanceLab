"""
PerformanceLab

Next Event Card
"""

import streamlit as st


def next_event_card(event):
    """
    Displays the next sporting event.
    """

    if event is None or event.name is None:

        st.info(
            "No upcoming events."
        )

        return

    st.markdown(
        f"### {event.name}"
    )

    subtitle = []

    if event.sport:
        subtitle.append(event.sport)

    if event.distance is not None:
        subtitle.append(f"{event.distance:g} km")

    if subtitle:
        st.caption(" · ".join(subtitle))

    left, right = st.columns(2)

    with left:

        if event.event_date is not None:
            value = event.event_date.strftime("%d %b %Y")
        else:
            value = "-"

        st.metric(
            "Date",
            value,
        )

    with right:

        if event.days_remaining is None:

            value = "-"

        elif event.days_remaining == 0:

            value = "Today"

        elif event.days_remaining == 1:

            value = "Tomorrow"

        elif event.days_remaining <= 7:

            value = f"{event.days_remaining} days (Race Week)"

        else:

            value = f"{event.days_remaining} days"

        st.metric(
            "Countdown",
            value,
        )

    if event.location:

        location = event.location

        if event.country:
            location += f", {event.country}"

        st.caption(
            f"📍 {location}"
        )

    if event.priority:

        st.caption(
            f"🎯 Priority {event.priority}"
        )

    if event.target_time:

        st.caption(
            f"⏱️ Target {event.target_time}"
        )