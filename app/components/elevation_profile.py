"""
PerformanceLab

Elevation Profile Component.
"""

import pandas as pd
import streamlit as st

from performancelab.presentation import (
    elevation_maximum,
    elevation_minimum,
    elevation_profile,
    has_elevation_profile,
)


# ======================================================
# Elevation profile
# ======================================================

def show_elevation_profile(
    workout,
) -> None:

    """
    Displays the workout elevation profile.
    """

    if not has_elevation_profile(
        workout
    ):

        return

    st.divider()

    st.subheader(
        "Elevation profile"
    )

    minimum = elevation_minimum(
        workout
    )

    maximum = elevation_maximum(
        workout
    )

    column_1, column_2 = st.columns(2)

    column_1.metric(

        "Minimum",

        f"{minimum:.0f} m",

    )

    column_2.metric(

        "Maximum",

        f"{maximum:.0f} m",

    )

    profile = elevation_profile(
        workout
    )

    chart = pd.DataFrame(

        {

            "Distance (km)": [

                point["distance_km"]

                for point in profile

            ],

            "Elevation (m)": [

                point["elevation"]

                for point in profile

            ],

        }

    )

    chart = chart.set_index(
        "Distance (km)"
    )

    st.area_chart(
        chart,
    )