"""
PerformanceLab

Manual Workout Form.

Internal component.
"""

from datetime import date
from datetime import timedelta

import streamlit as st

from services import (
    create_workout,
)


# ======================================================
# Manual workout form
# ======================================================

def show_manual_workout_form(
    athlete,
):

    """
    Displays the manual workout form.
    """

    with st.form(

        "manual_workout_form",

        clear_on_submit=True,

    ):

        title = st.text_input(

            "Title",

            placeholder="Morning run",

        )

        sport = st.selectbox(

            "Sport",

            options=[

                "Running",

                "Cycling",

                "Swimming",

                "Walking",

                "Hiking",

                "Strength",

                "Other",

            ],

        )

        workout_date = st.date_input(

            "Date",

            value=date.today(),

        )

        distance_value = st.number_input(

            "Distance (km)",

            min_value=0.0,

            value=0.0,

            step=0.1,

        )

        duration_column_1, \
        duration_column_2 = (

            st.columns(2)

        )

        with duration_column_1:

            duration_hours = st.number_input(

                "Hours",

                min_value=0,

                value=0,

                step=1,

            )

        with duration_column_2:

            duration_minutes = st.number_input(

                "Minutes",

                min_value=0,

                max_value=59,

                value=30,

                step=1,

            )

        elevation_value = st.number_input(

            "Elevation gain (m)",

            min_value=0.0,

            value=0.0,

            step=10.0,

        )

        rpe_value = st.slider(

            "RPE",

            min_value=0,

            max_value=10,

            value=5,

            step=1,

        )

        description = st.text_area(

            "Description",

            placeholder="Workout notes...",

        )

        submitted = st.form_submit_button(

            "Add workout",

            type="primary",

            use_container_width=True,

        )

        if submitted:

            elapsed = timedelta(

                hours=int(duration_hours),

                minutes=int(duration_minutes),

            )

            if elapsed.total_seconds() <= 0:

                st.error(

                    "Duration must be greater than zero."

                )

            else:

                workout = create_workout(

                    sport=sport,

                    workout_date=workout_date,

                    distance=(

                        float(distance_value)

                        if distance_value > 0

                        else None

                    ),

                    duration=elapsed,

                    elevation_gain=(

                        float(elevation_value)

                        if elevation_value > 0

                        else 0.0

                    ),

                    rpe=float(rpe_value),

                    title=title.strip(),

                    description=description.strip(),

                )

                athlete.history.add(

                    workout

                )

                st.session_state.notice = (

                    "Workout added successfully."

                )