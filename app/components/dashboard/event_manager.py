import streamlit as st


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

    events = sorted(
        athlete.events.entries,
        key=lambda event: event.date,
    )

    if not events:

        st.info(
            "No events have been added yet."
        )

    else:

        for event in events:

            st.markdown(
                f"**{event.name}**"
            )

            st.caption(
                event.date.strftime(
                    "%d %b %Y"
                )
            )

            st.divider()

    st.button(
        "Add Event",
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

    from performancelab.race.event import Event
    from performancelab.race.entry import EventEntry

    st.subheader(
        "Add Event"
    )

    event_name = st.text_input(
        "Event name",
    )

    event_date = st.date_input(
        "Date",
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
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        step=0.1,
    )

    elevation_gain = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        step=10.0,
    )

    priority = st.selectbox(
        "Priority",
        [
            "A",
            "B",
            "C",
        ],
    )

    location = st.text_input(
        "Location",
    )

    notes = st.text_area(
        "Notes",
    )

    save_col, cancel_col = st.columns(
        2
    )

    with save_col:

        if st.button(
            "Save",
            use_container_width=True,
        ):

            event = Event(
                name=event_name,
                date=event_date,
                sport=sport,
                distance=distance,
                elevation_gain=elevation_gain,
                location=location,
            )

            entry = EventEntry(
                event=event,
                priority=priority,
                notes=notes,
            )

            athlete.events.add(
                entry
            )

            st.session_state.show_add_event_form = False

            st.rerun()

    with cancel_col:

        if st.button(
            "Cancel",
            use_container_width=True,
        ):

            _close_add_event_form()

            st.rerun()