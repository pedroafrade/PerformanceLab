"""
PerformanceLab

Athlete Panel Component.
"""

from datetime import date

import streamlit as st


# ======================================================
# Constants
# ======================================================

_EDIT_STATE_KEY = "athlete_edit_mode"

_FORM_KEYS = (
    "athlete_edit_name",
    "athlete_edit_birth_date",
    "athlete_edit_gender",
    "athlete_edit_height",
    "athlete_edit_weight",
    "athlete_edit_ftp",
    "athlete_edit_max_hr",
    "athlete_edit_resting_hr",
)


# ======================================================
# Helpers
# ======================================================

def _clear_form_state() -> None:
    """
    Removes temporary athlete form values.
    """

    for key in _FORM_KEYS:

        st.session_state.pop(
            key,
            None,
        )


# ======================================================

def _start_editing(
    athlete,
) -> None:
    """
    Initializes the form with the current athlete values.
    """

    _clear_form_state()

    st.session_state[
        "athlete_edit_name"
    ] = athlete.name or ""

    st.session_state[
        "athlete_edit_birth_date"
    ] = athlete.birth_date

    st.session_state[
        "athlete_edit_gender"
    ] = athlete.gender or ""

    st.session_state[
        "athlete_edit_height"
    ] = float(
        athlete.height or 0.0
    )

    st.session_state[
        "athlete_edit_weight"
    ] = float(
        athlete.weight or 0.0
    )

    st.session_state[
        "athlete_edit_ftp"
    ] = float(
        athlete.ftp or 0.0
    )

    st.session_state[
        "athlete_edit_max_hr"
    ] = int(
        athlete.max_hr or 0
    )

    st.session_state[
        "athlete_edit_resting_hr"
    ] = int(
        athlete.resting_hr or 0
    )

    st.session_state[
        _EDIT_STATE_KEY
    ] = True


# ======================================================

def _optional_float(
    value,
):
    """
    Converts zero or negative numeric values to None.
    """

    value = float(value)

    return (
        value
        if value > 0
        else None
    )


# ======================================================

def _optional_int(
    value,
):
    """
    Converts zero or negative integer values to None.
    """

    value = int(value)

    return (
        value
        if value > 0
        else None
    )


# ======================================================

def _display_value(
    value,
    suffix: str = "",
) -> str:
    """
    Formats an optional athlete value for display.
    """

    if value is None or value == "":

        return "Not set"

    return f"{value}{suffix}"


# ======================================================
# View mode
# ======================================================

def _show_athlete_summary(
    athlete,
) -> None:
    """
    Displays the current athlete information.
    """

    st.subheader(
        athlete.name or "Unnamed athlete"
    )

    if athlete.birth_date is not None:

        today = date.today()

        age = (
            today.year
            - athlete.birth_date.year
            - (
                (
                    today.month,
                    today.day,
                )
                < (
                    athlete.birth_date.month,
                    athlete.birth_date.day,
                )
            )
        )

        st.caption(
            f"{age} years old"
        )

    st.write(
        "**Gender:** "
        f"{_display_value(athlete.gender)}"
    )

    st.write(
        "**Height:** "
        f"{_display_value(athlete.height, ' m')}"
    )

    st.write(
        "**Weight:** "
        f"{_display_value(athlete.weight, ' kg')}"
    )

    st.write(
        "**FTP:** "
        f"{_display_value(athlete.ftp, ' W')}"
    )

    st.write(
        "**Maximum heart rate:** "
        f"{_display_value(athlete.max_hr, ' bpm')}"
    )

    st.write(
        "**Resting heart rate:** "
        f"{_display_value(athlete.resting_hr, ' bpm')}"
    )

    if st.button(
        "Edit athlete",
        key="edit_athlete_button",
        use_container_width=True,
    ):

        _start_editing(
            athlete
        )

        st.rerun()


# ======================================================
# Edit mode
# ======================================================

def _show_athlete_form(
    athlete,
):
    """
    Displays the athlete editing form.
    """

    st.subheader(
        "Edit athlete"
    )

    gender_options = [
        "",
        "Male",
        "Female",
        "Other",
        "Prefer not to say",
    ]

    current_gender = st.session_state.get(
        "athlete_edit_gender",
        "",
    )

    if (
        current_gender
        and current_gender not in gender_options
    ):

        gender_options.insert(
            1,
            current_gender,
        )

    with st.form(
        "athlete_edit_form",
    ):

        name = st.text_input(
            "Name",
            key="athlete_edit_name",
        )

        birth_date = st.date_input(
            "Birth date",
            key="athlete_edit_birth_date",
            min_value=date(1900, 1, 1),
            max_value=date.today(),
        )

        gender = st.selectbox(
            "Gender",
            options=gender_options,
            index=gender_options.index(
                current_gender
            ),
            format_func=lambda value: (
                value
                if value
                else "Not set"
            ),
            key="athlete_edit_gender",
        )

        height = st.number_input(
            "Height (m)",
            min_value=0.0,
            max_value=3.0,
            step=0.01,
            format="%.2f",
            key="athlete_edit_height",
        )

        weight = st.number_input(
            "Weight (kg)",
            min_value=0.0,
            max_value=500.0,
            step=0.1,
            format="%.1f",
            key="athlete_edit_weight",
        )

        ftp = st.number_input(
            "FTP (W)",
            min_value=0.0,
            max_value=2000.0,
            step=1.0,
            key="athlete_edit_ftp",
        )

        max_hr = st.number_input(
            "Maximum heart rate",
            min_value=0,
            max_value=250,
            step=1,
            key="athlete_edit_max_hr",
        )

        resting_hr = st.number_input(
            "Resting heart rate",
            min_value=0,
            max_value=200,
            step=1,
            key="athlete_edit_resting_hr",
        )

        save_column, cancel_column = st.columns(
            2
        )

        with save_column:

            save = st.form_submit_button(
                "Save",
                type="primary",
                use_container_width=True,
            )

        with cancel_column:

            cancel = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    if cancel:

        st.session_state[
            _EDIT_STATE_KEY
        ] = False

        _clear_form_state()

        st.rerun()

    if save:

        cleaned_name = name.strip()

        if not cleaned_name:

            st.error(
                "Name cannot be empty."
            )

            return athlete

        if (
            max_hr > 0
            and resting_hr > 0
            and resting_hr >= max_hr
        ):

            st.error(
                "Resting heart rate must be lower "
                "than maximum heart rate."
            )

            return athlete

        athlete.name = cleaned_name

        athlete.birth_date = birth_date

        athlete.gender = gender

        athlete.height = _optional_float(
            height
        )

        athlete.weight = _optional_float(
            weight
        )

        athlete.ftp = _optional_float(
            ftp
        )

        athlete.max_hr = _optional_int(
            max_hr
        )

        athlete.resting_hr = _optional_int(
            resting_hr
        )

        st.session_state[
            _EDIT_STATE_KEY
        ] = False

        _clear_form_state()

        st.success(
            "Athlete data saved."
        )

        st.rerun()

    return athlete


# ======================================================
# Athlete panel
# ======================================================

def show_athlete_panel(
    athlete,
):
    """
    Displays athlete information and allows it to be edited.

    Parameters
    ----------
    athlete
        Athlete instance to update.

    Returns
    -------
    Athlete
        The same athlete instance after any edits.
    """

    st.header(
        "Athlete"
    )

    if _EDIT_STATE_KEY not in st.session_state:

        st.session_state[
            _EDIT_STATE_KEY
        ] = False

    if st.session_state[
        _EDIT_STATE_KEY
    ]:

        return _show_athlete_form(
            athlete
        )

    _show_athlete_summary(
        athlete
    )

    return athlete