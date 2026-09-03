"""
PerformanceLab

Route Map Component.
"""

from math import log2

import pydeck as pdk
import streamlit as st
from streamlit.components.v1 import html as components_html

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
    """Draw a thin, rounded route without changing recorded coordinates."""
    if not coordinates:
        return []
    route = [{"path": coordinates}]
    path_options = dict(
        data=route, get_path="path", width_units=pdk.types.String("pixels"),
        cap_rounded=True, joint_rounded=True, pickable=False,
    )
    return [
        pdk.Layer("PathLayer", id="route-line", get_width=1.6,
                  get_color=[25, 25, 25, 255], **path_options),
        pdk.Layer(
            "ScatterplotLayer", id="route-start",
            data=[{"position": coordinates[0], "label": "Start"}],
            get_position="position", radius_units=pdk.types.String("pixels"), get_radius=6,
            filled=True, stroked=True, get_fill_color=[22, 130, 78, 255],
            get_line_color=[255, 255, 255, 255],
            line_width_units=pdk.types.String("pixels"), get_line_width=2, pickable=True,
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


def _route_document(deck):
    """Use pydeck's renderer so view controllers and in-map buttons are honoured."""
    document = deck.to_html(as_string=True, open_browser=False)
    controls = """
    <style>
    html, body { margin: 0; padding: 0; overflow: hidden; border-radius: 10px; }
    .route-zoom-controls {
        position: absolute; right: 10px; top: 10px; z-index: 10;
        display: flex; flex-direction: column; border-radius: 6px;
        overflow: hidden; box-shadow: 0 1px 5px #0004;
    }
    .route-zoom-controls button {
        width: 34px; height: 34px; border: 0; background: #fff; color: #222;
        font: bold 22px sans-serif; cursor: pointer;
    }
    .route-zoom-controls button + button { border-top: 1px solid #ddd; }
    .route-zoom-controls button:focus-visible { outline: 2px solid #16824e; outline-offset: -3px; }
    </style>
    <script>
    if (deckInstance) {
        let routeView = {...jsonInput.initialViewState};
        deckInstance.setProps({
            useDevicePixels: true,
            viewState: routeView,
            onViewStateChange: ({viewState}) => {
                routeView = viewState;
                deckInstance.setProps({viewState: routeView});
            }
        });
        const controls = document.createElement('nav');
        controls.className = 'route-zoom-controls';
        controls.setAttribute('aria-label', 'Map zoom');
        controls.innerHTML = '<button type="button" aria-label="Zoom in" title="Zoom in">+</button>' +
                             '<button type="button" aria-label="Zoom out" title="Zoom out">−</button>';
        document.body.appendChild(controls);
        controls.querySelectorAll('button').forEach((button, index) => {
            button.addEventListener('click', () => {
                routeView = {...routeView, zoom: Math.max(1, Math.min(20, routeView.zoom + (index === 0 ? 1 : -1)))};
                deckInstance.setProps({viewState: routeView});
            });
        });
    }
    </script>
    """
    return document.replace("</html>", controls + "</html>")


def show_route_map(
    workout,
    *,
    height: int | None = None,
):
    """
    Displays the workout route.

    Pan by dragging; zoom using the in-map buttons or a touch pinch, not the mouse wheel.
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
            "scrollZoom": False,
            "doubleClickZoom": False,
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
        map_style="light",
        tooltip={"text": "{label}"},
    )

    st.markdown(
        """
        <style>
        .st-key-route_map_surface iframe {
            border: 1px solid rgba(128, 128, 128, 0.25);
            border-radius: 0.65rem;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True,
    )
    with st.container(key="route_map_surface"):
        components_html(_route_document(deck), height=height if height is not None else 420, scrolling=False)
