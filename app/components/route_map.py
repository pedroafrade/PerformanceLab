"""
PerformanceLab

Route Map Component.
"""

import pandas as pd
import pydeck as pdk
import streamlit as st

from performancelab.presentation import (

    has_route,

    route_center,

    route_coordinates,

)


# ======================================================
# Route map
# ======================================================

def show_route_map(workout):

    """
    Displays an interactive workout route.
    """

    if not has_route(workout):

        return

    coordinates = route_coordinates(

        workout

    )

    center = route_center(

        workout

    )

    if center is None:

        return

    route = pd.DataFrame(

        {

            "path": [

                coordinates

            ]

        }

    )

    layer = pdk.Layer(

        "PathLayer",

        data=route,

        get_path="path",

        get_width=5,

        pickable=False,

    )

    view = pdk.ViewState(

        latitude=center[0],

        longitude=center[1],

        zoom=13,

        pitch=0,

    )

    deck = pdk.Deck(

        layers=[

            layer

        ],

        initial_view_state=view,

        map_style="road",

    )

    st.pydeck_chart(

        deck,

        use_container_width=True,

    )