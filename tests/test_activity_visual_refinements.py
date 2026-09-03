"""Presentation-only refinements must preserve activity data and note saving."""
import ast
from pathlib import Path

import altair as alt
import pytest

COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


@pytest.mark.parametrize("metric,color", [
    ("Heart rate", "#e53935"), ("Power", "#9333ea"), ("Pace", "#f97316"),
])
@pytest.mark.parametrize("compare", [False, True])
def test_metric_colours_preserve_comparison_and_legend(metric, color, compare):
    tree = ast.parse((COMPONENTS / "activity_analysis.py").read_text(encoding="utf-8"))
    helper = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                  and n.name == "_metric_activity_color")
    scope = {"alt": alt}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), "colours", "exec"), scope)
    labels = ["Current", "Historical"] if compare else ["Current"]
    rows = [{"Activity": label} for label in labels]
    spec = scope["_metric_activity_color"](metric, rows, alt.Legend()).to_dict()
    assert spec["scale"]["domain"] == labels
    assert spec["scale"]["range"] == [color, "#2563eb"]
    assert spec["field"] == "Activity"


def test_coach_heading_has_no_activity_title():
    source = (COMPONENTS / "activities_page.py").read_text(encoding="utf-8")
    assert "activities-coach-heading" in source
    assert "activities-coach-activity" not in source
    assert "coach_activity_title" not in source


def test_notes_keep_save_callback_and_fixed_bottom_slot():
    tree = ast.parse((COMPONENTS / "activities_page.py").read_text(encoding="utf-8"))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)]
    notes = next(n for n in calls if isinstance(n.func, ast.Attribute)
                 and n.func.attr == "text_area" and n.args
                 and isinstance(n.args[0], ast.Constant)
                 and n.args[0].value == "Information for the Training Coach")
    assert next(k.value.value for k in notes.keywords if k.arg == "height") == 152
    save = next(n for n in calls if isinstance(n.func, ast.Attribute)
                and n.func.attr == "button" and n.args
                and isinstance(n.args[0], ast.Constant)
                and n.args[0].value == "Save information")
    assert next(ast.unparse(k.value) for k in save.keywords
                if k.arg == "on_click") == "_save_activity_coach_notes"
    slot = next(n for n in calls if any(k.arg == "key" and
                isinstance(k.value, ast.Constant) and k.value.value == "activities_bottom_slot"
                for k in n.keywords))
    assert next(k.value.value for k in slot.keywords if k.arg == "height") == 268


def test_map_has_no_legend_or_white_route_outline():
    source = (COMPONENTS / "route_map.py").read_text(encoding="utf-8")
    assert "route-map-legend" not in source
    assert "route-outline" not in source
    assert "useDevicePixels: true" in source
