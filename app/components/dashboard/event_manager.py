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
    st.session_state.selected_event = None
    st.session_state.event_to_delete = None

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
    if "event_to_delete" not in st.session_state:
        st.session_state.event_to_delete = None

    if "show_add_event_form" not in st.session_state:

        st.session_state.show_add_event_form = False

    if "selected_event" not in st.session_state:

        st.session_state.selected_event = None

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

            edit_col, delete_col = st.columns(
                2,
            )

            with edit_col:

                st.button(
                    "Edit",
                    key=f"edit-{id(entry)}",
                    use_container_width=True,
                    on_click=_open_edit_event_form,
                    args=(entry,),
                )

            with delete_col:

                st.button(
                    "Delete",
                    key=f"delete-{id(entry)}",
                    use_container_width=True,
                    on_click=_confirm_delete_event,
                    args=(entry,),
                )

            st.divider()
    if st.session_state.event_to_delete is not None:

        st.warning("Delete this event?")

        yes_col, no_col = st.columns(2)

        with yes_col:

            if st.button(
                "Yes",
                key="confirm-delete-event",
                use_container_width=True,
            ):

                _delete_event(
                    athlete,
                    st.session_state.event_to_delete,
                )

        with no_col:

            if st.button(
                "No",
                key="cancel-delete-event",
                use_container_width=True,
            ):

                st.session_state.event_to_delete = None
                st.rerun()

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

    st.session_state.selected_event = None
    st.session_state.event_to_delete = None
    st.session_state.show_add_event_form = True


def _open_edit_event_form(
    entry,
) -> None:
    """
    Opens the form in edit mode.
    """

    st.session_state.selected_event = entry
    st.session_state.event_to_delete = None
    st.session_state.show_add_event_form = True


def _close_add_event_form() -> None:
    """
    Returns to the event list.
    """

    st.session_state.selected_event = None
    st.session_state.event_to_delete = None
    st.session_state.show_add_event_form = False


def _delete_event(
    athlete,
    entry,
) -> None:
    """
    Deletes an event.
    """

    athlete.events.remove(
        entry
    )

    st.session_state.event_to_delete = None
    st.session_state.selected_event = None
    st.session_state.show_add_event_form = False

    st.rerun()


def _confirm_delete_event(entry) -> None:
    """
    Opens the delete confirmation.
    """

    st.session_state.event_to_delete = entry

def _show_add_event_form(
    athlete,
) -> None:
    """
    Displays the Add Event or Edit Event form.
    """

    entry = st.session_state.selected_event

    is_edit = entry is not None

    event = entry.event if is_edit else None

    st.subheader(
        "Edit Event" if is_edit else "Add Event"
    )

    event_name = st.text_input(
        "Event name",
        value=event.name if is_edit else "",
        key="event-name",
    )

    event_date = st.date_input(
        "Date",
        value=event.date if is_edit else None,
        key="event-date",
    )

    sports = [
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
    ]

    sport = st.selectbox(
        "Sport",
        sports,
        index=(
            sports.index(event.sport)
            if is_edit and event.sport in sports
            else 0
        ),
        key="event-sport",
    )

    distance = st.number_input(
        "Distance (km)",
        min_value=0.0,
        value=event.distance if is_edit else 0.0,
        step=0.1,
        key="event-distance",
    )

    elevation_gain = st.number_input(
        "Elevation gain (m)",
        min_value=0.0,
        value=event.elevation_gain if is_edit else 0.0,
        step=10.0,
        key="event-elevation-gain",
    )

    priorities = [
        "A",
        "B",
        "C",
    ]

    priority = st.selectbox(
        "Priority",
        priorities,
        index=(
            priorities.index(entry.priority)
            if is_edit and entry.priority in priorities
            else 0
        ),
        key="event-priority",
    )

    location = st.text_input(
        "Location",
        value=event.location if is_edit else "",
        key="event-location",
    )

    country = st.text_input(
        "Country",
        value=event.country if is_edit else "",
        key="event-country",
    )

    notes = st.text_area(
        "Notes",
        value=entry.notes if is_edit else "",
        key="event-notes",
    )

    save_col, cancel_col = st.columns(
        2
    )

    with save_col:

        if st.button(
            "Update" if is_edit else "Save",
            key="event-save",
            use_container_width=True,
        ):

            if not event_name.strip():

                st.error(
                    "Event name is required."
                )

                return

            if is_edit:

                entry.event.name = event_name.strip()
                entry.event.date = event_date
                entry.event.sport = sport
                entry.event.distance = distance
                entry.event.elevation_gain = elevation_gain
                entry.event.location = location.strip()
                entry.event.country = country.strip()

                entry.priority = priority
                entry.notes = notes.strip()

                athlete.events._sort()

            else:

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

            st.session_state.selected_event = None
            st.session_state.show_add_event_form = False

            st.rerun()

    with cancel_col:

        st.button(
            "Cancel",
            key="event-cancel",
            use_container_width=True,
            on_click=_close_add_event_form,
        )