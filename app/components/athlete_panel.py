"""
PerformanceLab

Athlete Panel Component.
"""

import streamlit as st


# ======================================================
# Athlete panel
# ======================================================

def show_athlete_panel(
    athlete,
):

    """
    Displays editable athlete information.

    Parameters
    ----------
    athlete
        Athlete instance to update.

    Returns
    -------
    Athlete
        The same athlete instance after any edits.
    """

    st.header("Athlete")

    athlete.name = st.text_input(
        "Name",
        value=athlete.name or "",
        key="athlete_name",
    )

    weight_value = st.number_input(
        "Weight (kg)",
        min_value=0.0,
        value=float(
            athlete.weight or 0.0
        ),
        step=0.1,
        key="athlete_weight",
    )

    athlete.weight = (
        float(weight_value)
        if weight_value > 0
        else None
    )

    ftp_value = st.number_input(
        "FTP (W)",
        min_value=0.0,
        value=float(
            athlete.ftp or 0.0
        ),
        step=1.0,
        key="athlete_ftp",
    )

    athlete.ftp = (
        float(ftp_value)
        if ftp_value > 0
        else None
    )

    max_hr_value = st.number_input(
        "Maximum heart rate",
        min_value=0,
        value=int(
            athlete.max_hr or 0
        ),
        step=1,
        key="athlete_max_hr",
    )

    athlete.max_hr = (
        int(max_hr_value)
        if max_hr_value > 0
        else None
    )

    resting_hr_value = st.number_input(
        "Resting heart rate",
        min_value=0,
        value=int(
            athlete.resting_hr or 0
        ),
        step=1,
        key="athlete_resting_hr",
    )

    athlete.resting_hr = (
        int(resting_hr_value)
        if resting_hr_value > 0
        else None
    )

    return athlete