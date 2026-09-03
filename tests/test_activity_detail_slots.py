"""Regression coverage for the activity utility column and map controls."""
import ast
from pathlib import Path

COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


def container_key(node):
    if not isinstance(node, ast.With):
        return None
    call = node.items[0].context_expr
    if not isinstance(call, ast.Call):
        return None
    return next((k.value.value for k in call.keywords
                 if k.arg == "key" and isinstance(k.value, ast.Constant)), None)


def test_lower_slot_swaps_notes_and_summary_instead_of_stacking_them():
    tree = ast.parse((COMPONENTS / "activities_page.py").read_text(encoding="utf-8"))
    utility = next(n for n in ast.walk(tree) if container_key(n) == "activities_utility")
    assert [container_key(n) for n in utility.body] == [
        "activity_coach_card", "activities_bottom_slot"]
    assert not any(k.arg == "height" for k in utility.items[0].context_expr.keywords)
    coach, bottom = utility.body
    heights = [next(k.value.value for k in n.items[0].context_expr.keywords
                    if k.arg == "height") for n in (coach, bottom)]
    assert heights == [440, 268]
    conditional = bottom.body[0]
    assert isinstance(conditional, ast.If)
    assert ast.unparse(conditional.test) == "selected_workout is not None"
    assert container_key(conditional.body[0]) == "activity_coach_notes"
    assert "_show_activity_summary" in ast.unparse(conditional.orelse[0])
    assert "_show_activity_summary" not in ast.unparse(conditional.body[0])


def test_exported_map_has_usable_buttons_and_disabled_wheel_zoom():
    import pydeck as pdk
    tree = ast.parse((COMPONENTS / "route_map.py").read_text(encoding="utf-8"))
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "_route_document")
    scope = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), "route_map.py", "exec"), scope)
    deck = pdk.Deck(map_style="light", initial_view_state=pdk.ViewState(
        latitude=38.7, longitude=-9.4, zoom=10), views=[pdk.View(
            type="MapView", controller={"scrollZoom": False, "dragPan": True})])
    document = scope["_route_document"](deck)
    assert '"scrollZoom": false' in document
    assert "const deckInstance" in document and "const jsonInput" in document
    assert 'aria-label="Zoom in"' in document
    assert 'aria-label="Zoom out"' in document
    assert "addEventListener('click'" in document
    assert "deckInstance.setProps({viewState: routeView})" in document


def test_no_similar_route_message_is_right_aligned():
    tree = ast.parse((COMPONENTS / "activity_analysis.py").read_text(encoding="utf-8"))
    literals = [n.value for n in ast.walk(tree)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)]
    message = next(value for value in literals
                   if "No sufficiently similar historical route was found." in value)
    assert "text-align: right" in message
