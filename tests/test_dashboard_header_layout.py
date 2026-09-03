"""Header parity and bounded dashboard cards without hiding overflow."""
import ast
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "app/components"


def test_development_header_matches_today_typography():
    development = (ROOT / "development_page.py").read_text(encoding="utf-8")
    today = (ROOT / "today_page.py").read_text(encoding="utf-8")
    for suffix in ("header", "title", "subtitle"):
        def declarations(source, prefix):
            match = re.search(r"\." + prefix + "-page-" + suffix + r"\s*\{([^}]+)\}", source)
            return " ".join(match.group(1).split())
        assert declarations(development, "development") == declarations(today, "today")


def test_development_first_output_contains_header_and_responsive_styles():
    tree = ast.parse((ROOT / "development_page.py").read_text(encoding="utf-8"))
    show = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "show_development_page")
    calls = [n.value for n in show.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    first = next(n for n in calls if isinstance(n.func, ast.Attribute) and n.func.attr == "markdown")
    text = first.args[0].value
    assert 'class="development-page-header"' in text
    assert ".st-key-development_load_form_mobile" in text
    assert "padding-top: 3.65rem" in text


def test_dashboard_card_heights_and_scroll_are_native():
    source = (ROOT / "dashboard/dashboard_view.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    constants = {n.targets[0].id: n.value.value for n in tree.body
                 if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)}
    assert constants["FIRST_ROW_HEIGHT"] == 330
    assert constants["SECOND_ROW_HEIGHT"] == 400
    heights = [k.value.id for n in ast.walk(tree) if isinstance(n, ast.Call)
               and isinstance(n.func, ast.Name) and n.func.id == "dashboard_widget"
               for k in n.keywords if k.arg == "height"]
    assert heights.count("FIRST_ROW_HEIGHT") == 3
    assert heights.count("SECOND_ROW_HEIGHT") == 6
    assert "overflow:hidden" not in source and "overflow: hidden" not in source
    assert "padding-bottom: 1.25rem" in source


def test_weekly_timeline_uses_full_content_width():
    source = (ROOT / "dashboard/cards/planning_card.py").read_text(encoding="utf-8")
    assert "timeline_columns" not in source
    assert "selector_columns" in source
    assert "phase_timeline_html(" in source
