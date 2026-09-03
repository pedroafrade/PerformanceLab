"""Validate rendered chart specifications without changing training calculations."""
import ast
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace

import altair as alt
import pytest


def chart_scope():
    path = Path(__file__).resolve().parents[1] / "app/components/development_page.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = {"_development_chart_rows", "_daily_load_chart_rows",
             "_mobile_chart_cutoff", "_mobile_chart_predicate",
             "_daily_training_load_chart", "_development_load_form_chart"}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    scope = {"alt": alt, "timedelta": timedelta}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), scope)
    return scope


@pytest.mark.parametrize("mobile", [False, True])
@pytest.mark.parametrize("count", [0, 1, 90])
def test_chart_legends_and_series_keep_correct_axes(mobile, count):
    data = SimpleNamespace(
        dates=[date(2026, 1, 1) + timedelta(days=i) for i in range(count)],
        fitness=[20] * count, fatigue=[30] * count, form=[-10] * count,
        daily_load=[40] * count,
    )
    scope = chart_scope()
    spec = scope["_development_load_form_chart"](data, mobile=mobile).to_dict()
    load, form = spec["layer"][:2]
    assert load["encoding"]["color"]["scale"] == form["encoding"]["color"]["scale"]
    assert form["encoding"]["color"]["scale"]["domain"] == ["Fatigue", "Fitness", "Form"]
    assert form["encoding"]["y"]["field"] == "Form"
    assert form["encoding"]["y"]["axis"]["orient"] == "right"
    daily = scope["_daily_training_load_chart"](data, mobile=mobile).to_dict()
    bars, average = daily["layer"]
    assert bars["encoding"]["color"]["scale"] == average["encoding"]["color"]["scale"]
    assert bars["encoding"]["color"]["scale"]["range"] == ["#4f86f7", "#f97316"]
    assert bars["encoding"]["y"]["field"] == "Training load"
    assert average["encoding"]["y"]["field"] == "rolling_load"
    assert any(t.get("frame") == [-6, 0] for t in average["transform"])
