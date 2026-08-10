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

def show_route_map(
    workout,
    *,
    height: int | None = None,
):
    """
    Displays the workout route.

    Panning remains available, while zooming is locked.
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

    fixed_zoom = 13

    view_state = pdk.ViewState(
        latitude=center[0],
        longitude=center[1],
        zoom=fixed_zoom,
        min_zoom=fixed_zoom,
        max_zoom=fixed_zoom,
        pitch=0,
    )

    map_view = pdk.View(
        type="MapView",
        controller={
            "dragPan": True,
            "dragRotate": False,
            "scrollZoom": False,
            "doubleClickZoom": False,
            "touchZoom": False,
            "keyboard": False,
        },
    )

    deck = pdk.Deck(
        layers=[
            layer
        ],
        views=[
            map_view
        ],
        initial_view_state=view_state,
        map_style="road",
    )

    st.pydeck_chart(
        deck,
        use_container_width=True,
        height=height,
    )