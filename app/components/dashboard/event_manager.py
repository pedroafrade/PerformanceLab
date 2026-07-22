"""
PerformanceLab

Athlete event manager.
"""

import streamlit as st

from performancelab.race.entry import EventEntry
from performancelab.race.event import Event


def open_event_manager(
    athlete,
) -> None:
    """
    Opens the athlete event manager from its initial screen.
    """

    st.session_state.show_add_event_form = False

    show_event_manager(
        athlete,
    )


@st.dialog("Manage Events")
def show_event_manager(
    athlete,
) -> None:
    """
    Displays the athlete event manager.
    """

    if "show_add_event_form" not in st.session_state:

        st.session_state.show_add_event_form = False

    if st.session_state.show_add_event_form:

        _show_add_event_form(
            athlete,
        )

        return

    st.subheader(
        "Upcoming Events"
    )

    events = list(
        athlete.events.upcoming
    )

    if not events:

        st.caption(
            "No events have been added yet."
        )

    else:

        for entry in events:

            event = entry.event

            st.markdown(
                f"**{event.name}**"
            )

            details = []

            if event.date is not None:

                details.append(
                    event.date.strftime(
                        "%d %b %Y"
                    )
                )

            if event.sport:

                details.append(
                    event.sport
                )

            if event.distance is not None:

                details.append(
                    f"{event.distance:g} km"
                )

            if details:

                st.caption(
                    " · ".join(
                        details
                    )
                )

            st.divider()

    st.button(
        "Add Event",
        key="event-manager-add-event",
        use_container_width=True,
        on_click=_open_add_event_form,
    )


def _open_add_event_form() -> None:
    """
    Switches the event manager to the Add Event form.
    """

    st.session_state.show_add_event_form = True


def _close_add_event_form() -> None:
    """
    Returns to the event list.
    """

    st.session_state.show_add_event_form = False


def _show_add_event_form(
    athlete,
) -> None:
    """
    Displays the Add Event form.
    """

    st.subheader(
        "Add Event"
    )

    event_name = st.text_input(
        "Event name",
        key="event-name",
    )

    event_date = st.date_input(
        "Date",
        key="event-date",
    )

    sport = st.selectbox(
        "Sport",
        [
            "Road Running",
            "Trail Running",
            "Track Running",
            "Cross Country",
            "Mountain Running",
            "Cycling",
            "Mountain Biking",
            "Swimming",
            "Triathlon",
            "Duathlon",
            "Other",
        ],
        key="event-sport",
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        step=0.1,
        key="event-distance",
    )

    elevation_gain = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        step=10.0,
        key="event-elevation-gain",
    )

    priority = st.selectbox(
        "Priority",
        [
            "A",
            "B",
            "C",
        ],
        key="event-priority",
    )

    location = st.text_input(
        "Location",
        key="event-location",
    )

    country = st.text_input(
        "Country",
        key="event-country",
    )

    notes = st.text_area(
        "Notes",
        key="event-notes",
    )

    save_col, cancel_col = st.columns(
        2
    )

    with save_col:

        if st.button(
            "Save",
            key="event-save",
            use_container_width=True,
        ):

            if not event_name.strip():

                st.error(
                    "Event name is required."
                )

                return

            event = Event(
                name=event_name.strip(),
                date=event_date,
                sport=sport,
                distance=distance,
                elevation_gain=elevation_gain,
                location=location.strip(),
                country=country.strip(),
            )

            entry = EventEntry(
                event=event,
                priority=priority,
                notes=notes.strip(),
            )

            athlete.events.add(
                entry
            )

            st.session_state.show_add_event_form = False

            st.rerun()

    with cancel_col:

        st.button(
            "Cancel",
            key="event-cancel",
            use_container_width=True,
            on_click=_close_add_event_form,
        )