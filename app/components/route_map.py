"""
PerformanceLab

Route Map Component.
"""

from math import log2

import pandas as pd
import pydeck as pdk
import streamlit as st

from performancelab.presentation import (
    has_route,
    route_coordinates,
)


# ======================================================
# Route map
# ======================================================
def _route_view(
    coordinates,
) -> tuple[
    float,
    float,
    float,
]:
    """
    Returns a map centre and zoom that contain the
    complete recorded route.
    """

    longitudes = [
        coordinate[0]
        for coordinate in coordinates
    ]

    latitudes = [
        coordinate[1]
        for coordinate in coordinates
    ]

    minimum_longitude = min(
        longitudes
    )
    maximum_longitude = max(
        longitudes
    )
    minimum_latitude = min(
        latitudes
    )
    maximum_latitude = max(
        latitudes
    )

    longitude = (
        minimum_longitude
        + maximum_longitude
    ) / 2

    latitude = (
        minimum_latitude
        + maximum_latitude
    ) / 2

    longitude_span = (
        maximum_longitude
        - minimum_longitude
    )

    latitude_span = (
        maximum_latitude
        - minimum_latitude
    )

    if (
        longitude_span <= 0
        and latitude_span <= 0
    ):
        return (
            latitude,
            longitude,
            16.0,
        )

    longitude_zoom = log2(
        360
        / max(
            longitude_span,
            0.000001,
        )
    )

    latitude_zoom = log2(
        180
        / max(
            latitude_span,
            0.000001,
        )
    )

    zoom = (
        min(
            longitude_zoom,
            latitude_zoom,
        )
        - 0.9
    )

    zoom = max(
        1.0,
        min(
            zoom,
            18.0,
        ),
    )

    return (
        latitude,
        longitude,
        zoom,
    )

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

    (
        latitude,
        longitude,
        route_zoom,
    ) = _route_view(
        coordinates
    )

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

    view_state = pdk.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=route_zoom,
        min_zoom=1,
        max_zoom=20,
        pitch=0,
    )

    map_view = pdk.View(
        type="MapView",
        controller={
            "dragPan": True,
            "dragRotate": False,
            "scrollZoom": True,
            "doubleClickZoom": True,
            "touchZoom": True,
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