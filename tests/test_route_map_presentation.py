"""Route styling without altering coordinates or introducing another map provider."""
import ast
from copy import deepcopy
from math import log2
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


def load_route(st=None, has_route=lambda workout: True, coordinates=()):
    tree = ast.parse((COMPONENTS / "route_map.py").read_text(encoding="utf-8"))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
    pdk = SimpleNamespace(
        types=SimpleNamespace(String=lambda value: value),
        Layer=lambda kind, **kwargs: {"type": kind, **kwargs},
        Deck=lambda **kwargs: kwargs,
        ViewState=lambda **kwargs: kwargs,
        View=lambda **kwargs: kwargs,
    )
    scope = {"log2": log2, "pdk": pdk, "st": st,
             "components_html": MagicMock(),
             "has_route": has_route, "route_coordinates": lambda workout: coordinates}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "route_map.py", "exec"), scope)
    scope["_route_document"] = lambda deck: deck
    return scope


@pytest.mark.parametrize("coordinates", [
    [[-9.4, 38.7], [-9.2, 38.8]],
    [[-9.4, 38.7], [-9.2, 38.8], [-9.4, 38.7]],
    [[-9.4, 38.7]],
])
def test_layers_preserve_route_and_endpoint_coordinates(coordinates):
    original = deepcopy(coordinates)
    route, start, finish = load_route()["_route_layers"](coordinates)
    assert route["data"][0]["path"] == original
    assert start["data"][0]["position"] == original[0]
    assert finish["data"][0]["position"] == original[-1]
    assert coordinates == original
    assert route["get_color"] == [25, 25, 25, 255]
    assert route["get_width"] == 1.6
    assert route["cap_rounded"] and route["joint_rounded"]
    assert route["width_units"] == "pixels"
    assert start["filled"] is True and finish["filled"] is True
    assert start["get_radius"] == finish["get_radius"] == 6
    assert start["get_fill_color"] == [22, 130, 78, 255]


def test_empty_route_has_no_layers():
    assert load_route()["_route_layers"]([]) == []


def test_real_pydeck_serializes_route_width_and_marker_units():
    import json
    import pydeck as pdk

    scope = load_route()
    scope["pdk"] = pdk
    layers = scope["_route_layers"]([[-9.4, 38.7], [-9.2, 38.8]])
    payload = json.loads(pdk.Deck(layers=layers, map_style="light").to_json())
    assert len(payload["layers"]) == 3
    assert payload["layers"][0]["widthUnits"] == "pixels"
    assert payload["layers"][0]["getColor"] == [25, 25, 25, 255]
    assert payload["layers"][1]["radiusUnits"] == "pixels"
    assert payload["layers"][1]["getRadius"] == 6
    assert payload["layers"][2]["getRadius"] == 6


@pytest.mark.parametrize("available,coords", [(False, []), (True, [])])
def test_no_chart_for_missing_coordinates(available, coords):
    st = MagicMock()
    load_route(st, lambda workout: available, coords)["show_route_map"](object())
    st.pydeck_chart.assert_not_called()
    st.container.assert_not_called()


def test_provider_view_height_and_controls_are_preserved():
    st = MagicMock()
    coordinates = [[-9.4, 38.7], [-9.2, 38.8]]
    scope = load_route(st, coordinates=coordinates)
    scope["show_route_map"](object(), height=260)
    deck = scope["components_html"].call_args.args[0]
    assert deck["map_style"] == "light"
    assert deck["initial_view_state"]["pitch"] == 0
    assert deck["tooltip"] == {"text": "{label}"}
    assert deck["views"][0]["controller"]["scrollZoom"] is False
    assert deck["views"][0]["controller"]["doubleClickZoom"] is False
    assert deck["views"][0]["controller"]["dragPan"] is True
    assert scope["components_html"].call_args.kwargs["height"] == 260
    assert scope["components_html"].call_args.kwargs["scrolling"] is False
    st.html.assert_not_called()
    css = st.markdown.call_args.args[0]
    assert '.st-key-route_map_surface iframe' in css
    assert "border-radius: 0.65rem" in css


def test_summary_omits_date_caption_without_removing_filters_or_warnings():
    tree = ast.parse((COMPONENTS / "activities_page.py").read_text(encoding="utf-8"))
    show = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_show_activity_summary")
    literals = [n.value for n in ast.walk(show) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    assert not any("Independent of list filters" in value or "→" in value for value in literals)
    assert "activities_summary_period" in literals and "activities_summary_sport" in literals
    assert any("No activities" in value for value in literals)
    assert any("measurements are missing" in value for value in literals)
