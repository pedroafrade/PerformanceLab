"""Calendar owns the download; the existing complete-plan exporter is retained."""
import ast
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest


COMPONENTS = Path(__file__).resolve().parents[1] / "app/components"


def calendar_tree():
    return ast.parse((COMPONENTS / "calendar_page.py").read_text(encoding="utf-8"))


@pytest.mark.parametrize("has_plan", [False, True])
def test_calendar_export_preserves_download_contract(has_plan):
    node = next(n for n in calendar_tree().body
                if isinstance(n, ast.FunctionDef) and n.name == "_show_calendar_export")
    st = MagicMock()
    presenter = MagicMock()
    plan = SimpleNamespace(weeks=(object(), object()) if has_plan else ())
    presenter.return_value.build.return_value = plan
    exporter = MagicMock(return_value="BEGIN:VCALENDAR\r\nEND:VCALENDAR\r\n")
    scope = {"st": st, "date": date, "PlanPresenter": presenter,
             "_plan_calendar_ics": exporter}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "calendar_page.py", "exec"), scope)
    athlete = SimpleNamespace(training_plan=object(), history=object())
    reference_day = date(2026, 9, 3)
    scope["_show_calendar_export"](athlete, reference_day=reference_day)
    presenter.assert_called_once_with(plan=athlete.training_plan, history=athlete.history)
    presenter.return_value.build.assert_called_once_with(reference_day=reference_day)
    options = st.download_button.call_args.kwargs
    assert options["file_name"] == "performancelab-plan.ics"
    assert options["mime"] == "text/calendar; charset=utf-8"
    assert options["use_container_width"] is True
    assert options["disabled"] is (not has_plan)
    assert options["data"] == (exporter.return_value if has_plan else "")
    assert "complete training plan" in options["help"]
    if has_plan:
        exporter.assert_called_once_with(plan)
    else:
        exporter.assert_not_called()


def test_calendar_export_follows_month_navigation_and_uses_today():
    column = next(n for n in ast.walk(calendar_tree()) if isinstance(n, ast.With)
                  and any(isinstance(i.context_expr, ast.Name)
                          and i.context_expr.id == "sidebar_column" for i in n.items))
    calls = {n.func.id: n for n in ast.walk(column)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    export = calls["_show_calendar_export"]
    assert calls["_show_month_navigation"].lineno < export.lineno
    assert export.lineno < calls["_show_selected_day"].lineno
    reference = next(k.value for k in export.keywords if k.arg == "reference_day")
    assert isinstance(reference, ast.Name) and reference.id == "today"


def test_calendar_reuses_existing_exporter_without_duplicate_implementation():
    tree = calendar_tree()
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)]
    assert any(n.module == "plan_page" and any(a.name == "_plan_calendar_ics" for a in n.names)
               for n in imports)
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_plan_calendar_ics"
                   for n in tree.body)
