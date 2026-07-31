"""
PerformanceLab

Athlete Panel Component.
"""

from datetime import date

import streamlit as st

from performancelab.analysis import (
    HeartRateZone,
)

from performancelab.training.config import AthleteAvailability


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
    "athlete_edit_threshold_hr",
    "athlete_edit_manual_hr_zones",
    "athlete_edit_z1_lower",
    "athlete_edit_z1_upper",
    "athlete_edit_z2_lower",
    "athlete_edit_z2_upper",
    "athlete_edit_z3_lower",
    "athlete_edit_z3_upper",
    "athlete_edit_z4_lower",
    "athlete_edit_z4_upper",
    "athlete_edit_z5_lower",
    "athlete_edit_z5_upper",
    "athlete_edit_train_any_day",
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
        "athlete_edit_threshold_hr"
    ] = int(
        athlete.threshold_hr or 0
    )

    manual_zones = (
        athlete.manual_heart_rate_zones
    )

    heart_rate_profile = (
        athlete.analytics
        .heart_rate_profile
    )

    available_zones = (
        manual_zones
        if manual_zones
        else (
            heart_rate_profile.zones
            if heart_rate_profile is not None
            else ()
        )
    )

    zones_by_name = {
        zone.name: zone
        for zone in available_zones
    }

    st.session_state[
        "athlete_edit_manual_hr_zones"
    ] = bool(manual_zones)

    for zone_name in (
        "Z1",
        "Z2",
        "Z3",
        "Z4",
        "Z5",
    ):

        zone = zones_by_name.get(
            zone_name
        )

        lower_value = (
            zone.lower_bpm
            if zone is not None
            else 1
        )

        upper_value = (
            zone.upper_bpm
            if zone is not None
            else 1
        )

        normalized_name = (
            zone_name.lower()
        )

        st.session_state[
            f"athlete_edit_{normalized_name}_lower"
        ] = int(lower_value)

        st.session_state[
            f"athlete_edit_{normalized_name}_upper"
        ] = int(upper_value)

    st.session_state[
        "athlete_edit_train_any_day"
    ] = athlete.train_any_day

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

    st.write(
        "**Threshold heart rate:** "
        f"{_display_value(athlete.threshold_hr, ' bpm')}"
    )

    heart_rate_profile = (
        athlete.analytics
        .heart_rate_profile
    )

    st.caption(
        "Heart-rate training zones:"
    )

    if heart_rate_profile is None:

        st.caption(
            "Set maximum and resting heart rate "
            "to calculate training zones."
        )

    else:

        source = (
            "manually configured"
            if (
                heart_rate_profile
                .uses_manual_zones
            )
            else (
                "automatically calculated "
                "using Karvonen"
            )
        )

        for zone in heart_rate_profile.zones:

            st.write(
                f"**{zone.name}:** "
                f"{zone.lower_bpm}–"
                f"{zone.upper_bpm} bpm"
            )

        st.caption(
            f"Zone source: {source}"
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

    st.divider()

    st.subheader("Training availability")

    train_any_day = st.checkbox(
        "Available to train on any day",
        key="athlete_edit_train_any_day",
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

        threshold_hr = st.number_input(
            "Threshold heart rate",
            min_value=0,
            max_value=250,
            step=1,
            key="athlete_edit_threshold_hr",
            help=(
                "Heart rate that can be sustained "
                "around lactate threshold intensity. "
                "Use 0 when it is not known."
            ),
        )

        st.caption(
            "Heart-rate training zones:"
        )

        manual_zone_values = {}

        for zone_name in (
            "Z1",
            "Z2",
            "Z3",
            "Z4",
            "Z5",
        ):

            normalized_name = (
                zone_name.lower()
            )

            zone_column, lower_column, upper_column = (
                st.columns(
                    [1, 2, 2]
                )
            )

            with zone_column:

                st.write(
                    f"**{zone_name}**"
                )

            with lower_column:

                lower_bpm = st.number_input(
                    f"{zone_name} from",
                    min_value=1,
                    max_value=250,
                    step=1,
                    key=(
                        "athlete_edit_"
                        f"{normalized_name}_lower"
                    ),
                )

            with upper_column:

                upper_bpm = st.number_input(
                    f"{zone_name} to",
                    min_value=1,
                    max_value=250,
                    step=1,
                    key=(
                        "athlete_edit_"
                        f"{normalized_name}_upper"
                    ),
                )

            manual_zone_values[
                zone_name
            ] = (
                int(lower_bpm),
                int(upper_bpm),
            )

        use_manual_hr_zones = st.checkbox(
            "Use manually configured heart-rate zones",
            key="athlete_edit_manual_hr_zones",
            help=(
                "When disabled, these values are ignored "
                "and the zones are calculated automatically "
                "from maximum and resting heart rate."
            ),
        )

        if not train_any_day:

            st.caption(
                "Enter the maximum training time available on each day."
            )

            monday_minutes = st.number_input(
                "Monday (minutes)",
                min_value=0,
                max_value=300,
                step=15,
                value=athlete.availability.minutes_for(0),
            )

            tuesday_minutes = st.number_input(
                "Tuesday (minutes)",
                min_value=0,
                max_value=300,
                step=15,
                value=athlete.availability.minutes_for(1),
            )

            wednesday_minutes = st.number_input(
                "Wednesday (minutes)",
                min_value=0,
                max_value=300,
                step=15,
                value=athlete.availability.minutes_for(2),
            )

            thursday_minutes = st.number_input(
                "Thursday (minutes)",
                min_value=0,
                max_value=300,
                step=15,
                value=athlete.availability.minutes_for(3),
            )

            friday_minutes = st.number_input(
                "Friday (minutes)",
                min_value=0,
                max_value=300,
                step=15,
                value=athlete.availability.minutes_for(4),
            )

            saturday_minutes = st.number_input(
                "Saturday (minutes)",
                min_value=0,
                max_value=480,
                step=15,
                value=athlete.availability.minutes_for(5),
            )

            sunday_minutes = st.number_input(
                "Sunday (minutes)",
                min_value=0,
                max_value=480,
                step=15,
                value=athlete.availability.minutes_for(6),
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

        if (
            threshold_hr > 0
            and resting_hr > 0
            and threshold_hr <= resting_hr
        ):

            st.error(
                "Threshold heart rate must be higher "
                "than resting heart rate."
            )

            return athlete

        if (
            threshold_hr > 0
            and max_hr > 0
            and threshold_hr >= max_hr
        ):

            st.error(
                "Threshold heart rate must be lower "
                "than maximum heart rate."
            )

            return athlete

        manual_heart_rate_zones = ()

        if use_manual_hr_zones:

            built_zones = []
            previous_upper = None

            for zone_name in (
                "Z1",
                "Z2",
                "Z3",
                "Z4",
                "Z5",
            ):

                lower_bpm, upper_bpm = (
                    manual_zone_values[
                        zone_name
                    ]
                )

                if lower_bpm > upper_bpm:

                    st.error(
                        f"{zone_name} lower limit "
                        "cannot be higher than its "
                        "upper limit."
                    )

                    return athlete

                if (
                    previous_upper is not None
                    and lower_bpm < previous_upper
                ):

                    st.error(
                        f"{zone_name} overlaps the "
                        "previous heart-rate zone."
                    )

                    return athlete

                if (
                    max_hr > 0
                    and upper_bpm > max_hr
                ):

                    st.error(
                        f"{zone_name} cannot exceed "
                        "maximum heart rate."
                    )

                    return athlete

                built_zones.append(
                    HeartRateZone(
                        name=zone_name,
                        lower_bpm=lower_bpm,
                        upper_bpm=upper_bpm,
                    )
                )

                previous_upper = (
                    upper_bpm
                )

            manual_heart_rate_zones = tuple(
                built_zones
            )

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

        athlete.threshold_hr = _optional_int(
            threshold_hr
        )

        athlete.manual_heart_rate_zones = (
            manual_heart_rate_zones
        )

        athlete.analytics.invalidate_performance_profile()

        athlete.train_any_day = train_any_day

        if not train_any_day:
            athlete.availability = AthleteAvailability.from_minutes(
                monday=int(monday_minutes),
                tuesday=int(tuesday_minutes),
                wednesday=int(wednesday_minutes),
                thursday=int(thursday_minutes),
                friday=int(friday_minutes),
                saturday=int(saturday_minutes),
                sunday=int(sunday_minutes),
            )
    

        st.session_state[
            _EDIT_STATE_KEY
        ] = False

        _clear_form_state()

        st.session_state.notice = (
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