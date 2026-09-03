"""
PerformanceLab

Route Map Component.
"""

from math import log2

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

def _route_layers(coordinates):
    """Draw a cased route and concentric-compatible endpoint markers."""
    if not coordinates:
        return []
    route = [{"path": coordinates}]
    path_options = dict(
        data=route, get_path="path", width_units=pdk.types.String("pixels"),
        cap_rounded=True, joint_rounded=True, pickable=False,
    )
    return [
        pdk.Layer("PathLayer", id="route-outline", get_width=7,
                  get_color=[255, 255, 255, 230], **path_options),
        pdk.Layer("PathLayer", id="route-line", get_width=3.5,
                  get_color=[229, 57, 53, 255], **path_options),
        pdk.Layer(
            "ScatterplotLayer", id="route-start",
            data=[{"position": coordinates[0], "label": "Start"}],
            get_position="position", radius_units=pdk.types.String("pixels"), get_radius=11,
            filled=False, stroked=True, get_line_color=[22, 130, 78, 255],
            line_width_units=pdk.types.String("pixels"), get_line_width=3, pickable=True,
        ),
        pdk.Layer(
            "ScatterplotLayer", id="route-finish",
            data=[{"position": coordinates[-1], "label": "Finish"}],
            get_position="position", radius_units=pdk.types.String("pixels"), get_radius=6,
            filled=True, stroked=True, get_fill_color=[229, 57, 53, 255],
            get_line_color=[255, 255, 255, 255], line_width_units=pdk.types.String("pixels"),
            get_line_width=2, pickable=True,
        ),
    ]


def show_route_map(
    workout,
    *,
    height: int | None = None,
):
    """
    Displays the workout route.

    Panning and zooming remain available, with a flat map view.
    """

    if not has_route(workout):
        return

    coordinates = route_coordinates(
        workout
    )
    if not coordinates:
        return

    (
        latitude,
        longitude,
        route_zoom,
    ) = _route_view(
        coordinates
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
        layers=_route_layers(coordinates),
        views=[
            map_view
        ],
        initial_view_state=view_state,
        map_style="road",
        tooltip={"text": "{label}"},
    )

    st.markdown(
        """
        <style>
        .st-key-route_map_surface [data-testid="stDeckGlJsonChart"] {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 0.65rem;
            overflow: hidden;
        }
        .route-map-legend {
            display: flex; flex-wrap: wrap; gap: 0.8rem;
            align-items: center; font-size: 0.72rem; line-height: 1.4;
        }
        .route-map-legend span { display: inline-flex; align-items: center; gap: 0.35rem; }
        .route-map-start {
            width: 0.75rem; height: 0.75rem; border: 2px solid #16824e;
            border-radius: 50%; display: inline-block; box-sizing: border-box;
        }
        .route-map-finish {
            width: 0.55rem; height: 0.55rem; background: #e53935;
            border-radius: 50%; display: inline-block;
        }
        </style>
        """, unsafe_allow_html=True,
    )
    with st.container(key="route_map_surface"):
        st.pydeck_chart(deck, use_container_width=True, height=height)
        st.html(
            '<div class="route-map-legend">'
            '<span><i class="route-map-start" aria-hidden="true"></i>Start</span>'
            '<span><i class="route-map-finish" aria-hidden="true"></i>Finish</span>'
            '</div>'
        )
