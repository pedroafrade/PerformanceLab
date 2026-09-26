"""First-login setup for newly provisioned athlete accounts."""

from calendar import month_name
from datetime import date

import streamlit as st

from performancelab.race.entry import EventEntry
from performancelab.race.event import Event

from .import_panel import show_import_panel


_STEPS = (
    "Profile",
    "Metrics",
    "Events",
    "Training history",
    "Review",
)


def _optional_float(value):
    return float(value) if value and value > 0 else None


def _optional_int(value):
    return int(value) if value and value > 0 else None


def _save_step(athlete, *, step, on_save):
    athlete.onboarding_step = step
    on_save(athlete)
    st.rerun()


def _navigation(athlete, *, step, on_save, disabled=False):
    previous, spacer, skip = st.columns([1, 1, 1])
    with previous:
        if step > 1 and st.button(
            "Back",
            key=f"onboarding_back_{step}",
            use_container_width=True,
            disabled=disabled,
        ):
            _save_step(athlete, step=step - 1, on_save=on_save)
    with skip:
        if st.button(
            "Skip setup",
            key=f"onboarding_skip_{step}",
            use_container_width=True,
            disabled=disabled,
        ):
            athlete.onboarding_completed = True
            athlete.onboarding_step = 5
            on_save(athlete)
            st.rerun()


def _birth_date_inputs(current_value):
    """Render a birth date without the paged native year picker."""

    fallback = current_value or date(1990, 1, 1)
    supplied = st.checkbox(
        "Add birth date",
        value=current_value is not None,
    )
    year, month, day = st.columns(3)
    with year:
        selected_year = st.selectbox(
            "Year",
            range(date.today().year, 1899, -1),
            index=date.today().year - fallback.year,
        )
    with month:
        selected_month = st.selectbox(
            "Month",
            range(1, 13),
            index=fallback.month - 1,
            format_func=lambda value: month_name[value],
        )
    with day:
        selected_day = st.selectbox(
            "Day",
            range(1, 32),
            index=fallback.day - 1,
        )

    if not supplied:
        return None

    try:
        return date(selected_year, selected_month, selected_day)
    except ValueError:
        return False


def _profile_step(athlete, on_save):
    st.subheader("Tell us about you")
    st.caption("These details personalise training guidance. You can edit them later.")

    genders = ["", "Male", "Female", "Other", "Prefer not to say"]
    current_gender = athlete.gender if athlete.gender in genders else ""

    with st.form("onboarding_profile"):
        name = st.text_input("Name", value=athlete.name)
        birth_date = _birth_date_inputs(athlete.birth_date)
        gender = st.selectbox(
            "Gender",
            genders,
            index=genders.index(current_gender),
            format_func=lambda value: value or "Not set",
        )
        submitted = st.form_submit_button(
            "Save and continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not name.strip():
            st.error("Name is required.")
            return
        if birth_date is False:
            st.error("Enter a valid birth date.")
            return
        if birth_date is not None and birth_date > date.today():
            st.error("Birth date cannot be in the future.")
            return
        athlete.name = name.strip()
        athlete.birth_date = birth_date
        athlete.gender = gender
        _save_step(athlete, step=2, on_save=on_save)

    _navigation(athlete, step=1, on_save=on_save)


def _metrics_step(athlete, on_save):
    st.subheader("Current metrics")
    st.caption("Enter only values you know. Zero leaves a metric unset.")

    with st.form("onboarding_metrics"):
        height = st.number_input(
            "Height (m)",
            min_value=0.0,
            max_value=3.0,
            value=float(athlete.height or 0.0),
            step=0.01,
        )
        weight = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            max_value=500.0,
            value=float(athlete.weight or 0.0),
            step=0.1,
        )
        ftp = st.number_input(
            "Cycling FTP (W)",
            min_value=0.0,
            max_value=2000.0,
            value=float(athlete.ftp or 0.0),
            step=1.0,
        )
        max_hr = st.number_input(
            "Maximum heart rate",
            min_value=0,
            max_value=250,
            value=int(athlete.max_hr or 0),
            step=1,
        )
        resting_hr = st.number_input(
            "Resting heart rate",
            min_value=0,
            max_value=200,
            value=int(athlete.resting_hr or 0),
            step=1,
        )
        threshold_hr = st.number_input(
            "Threshold heart rate",
            min_value=0,
            max_value=250,
            value=int(athlete.threshold_hr or 0),
            step=1,
        )
        submitted = st.form_submit_button(
            "Save and continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if max_hr and resting_hr and resting_hr >= max_hr:
            st.error("Resting heart rate must be lower than maximum heart rate.")
            return
        if threshold_hr and resting_hr and threshold_hr <= resting_hr:
            st.error("Threshold heart rate must be higher than resting heart rate.")
            return
        if threshold_hr and max_hr and threshold_hr >= max_hr:
            st.error("Threshold heart rate must be lower than maximum heart rate.")
            return

        athlete.height = _optional_float(height)
        athlete.weight = _optional_float(weight)
        athlete.ftp = _optional_float(ftp)
        athlete.max_hr = _optional_int(max_hr)
        athlete.resting_hr = _optional_int(resting_hr)
        athlete.threshold_hr = _optional_int(threshold_hr)
        athlete.analytics.invalidate_performance_profile()
        _save_step(athlete, step=3, on_save=on_save)

    _navigation(athlete, step=2, on_save=on_save)


def _events_step(athlete, on_save):
    st.subheader("Upcoming events")
    st.caption("Add an important future race, or continue without one.")

    for entry in athlete.events.upcoming:
        details = [entry.event.date.isoformat() if entry.event.date else "Date not set"]
        if entry.event.distance:
            details.append(f"{entry.event.distance:g} km")
        st.write(f"**{entry.event.name}** — {' · '.join(details)}")

    with st.form("onboarding_event", clear_on_submit=True):
        name = st.text_input("Event name")
        event_date = st.date_input("Date", value=date.today())
        sport = st.selectbox(
            "Sport",
            [
                "Road Running", "Trail Running", "Track Running",
                "Cross Country", "Mountain Running", "Cycling",
                "Mountain Biking", "Swimming", "Triathlon",
                "Duathlon", "Other",
            ],
        )
        distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)
        priority = st.selectbox("Priority", ["A", "B", "C"])
        add_event = st.form_submit_button("Add event", use_container_width=True)

    if add_event:
        if not name.strip():
            st.error("Event name is required.")
            return
        if event_date < date.today():
            st.error("The event date must be today or later.")
            return
        athlete.events.add(
            EventEntry(
                event=Event(
                    name=name.strip(),
                    date=event_date,
                    sport=sport,
                    distance=_optional_float(distance),
                ),
                priority=priority,
            )
        )
        on_save(athlete)
        st.rerun()

    if st.button(
        "Continue",
        type="primary",
        key="onboarding_events_continue",
        use_container_width=True,
    ):
        _save_step(athlete, step=4, on_save=on_save)

    _navigation(athlete, step=3, on_save=on_save)


def _history_step(athlete, on_save, on_import_activities):
    st.subheader("Training history")
    st.caption(
        "Upload past activities to populate training load and development trends. "
        "Multiple supported files can be selected together."
    )

    mode_key = "onboarding_history_mode"
    completed_key = "onboarding_history_file_uploader_completed"
    mode = st.session_state.get(mode_key)

    if mode is None:
        upload, continue_without = st.columns(2)
        with upload:
            if st.button(
                "Upload activities",
                type="primary",
                key="onboarding_history_upload",
                use_container_width=True,
            ):
                st.session_state[mode_key] = "upload"
                st.session_state.pop(completed_key, None)
                st.rerun()
        with continue_without:
            if st.button(
                "Continue without activities",
                key="onboarding_history_without_upload",
                use_container_width=True,
            ):
                _save_step(athlete, step=5, on_save=on_save)

        _navigation(athlete, step=4, on_save=on_save)
        return

    upload_completed = st.session_state.get(completed_key, False)

    show_import_panel(
        athlete,
        on_import_activities=on_import_activities,
        key_prefix="onboarding_history",
    )

    if not upload_completed:
        st.info(
            "Choose the activity files and keep this page open. Navigation "
            "will become available after the complete batch finishes."
        )
        return

    if st.button(
        "Continue",
        type="primary",
        key="onboarding_history_continue",
        use_container_width=True,
    ):
        st.session_state.pop(mode_key, None)
        st.session_state.pop(completed_key, None)
        _save_step(athlete, step=5, on_save=on_save)

    _navigation(athlete, step=4, on_save=on_save)


def _review_step(athlete, on_save):
    st.subheader("Ready to start")
    st.write(f"**Name:** {athlete.name or 'Not set'}")
    st.write(f"**Activities imported:** {len(athlete.history)}")
    st.write(f"**Upcoming events:** {len(tuple(athlete.events.upcoming))}")
    metrics = sum(
        value is not None
        for value in (
            athlete.height, athlete.weight, athlete.ftp,
            athlete.max_hr, athlete.resting_hr, athlete.threshold_hr,
        )
    )
    st.write(f"**Metrics supplied:** {metrics} of 6")
    st.caption("Everything can be changed later in Settings, Calendar and Activities.")

    if st.button(
        "Finish setup",
        type="primary",
        key="onboarding_finish",
        use_container_width=True,
    ):
        athlete.onboarding_completed = True
        athlete.onboarding_step = 5
        on_save(athlete)
        st.rerun()

    _navigation(athlete, step=5, on_save=on_save)


@st.dialog("Set up your athlete profile", width="large")
def show_onboarding_dialog(
    athlete,
    *,
    on_save,
    on_import_activities,
):
    """Show the resumable setup flow for a newly provisioned athlete."""

    step = athlete.onboarding_step
    st.progress(step / len(_STEPS))
    st.caption(f"Step {step} of {len(_STEPS)} · {_STEPS[step - 1]}")

    if step == 1:
        _profile_step(athlete, on_save)
    elif step == 2:
        _metrics_step(athlete, on_save)
    elif step == 3:
        _events_step(athlete, on_save)
    elif step == 4:
        _history_step(athlete, on_save, on_import_activities)
    else:
        _review_step(athlete, on_save)
