"""Scoped spacing regressions for the read-only Settings profile."""
import ast
from pathlib import Path
from unittest.mock import MagicMock


def profile_css():
    path = Path(__file__).resolve().parents[1] / "app/components/settings_page.py"
    node = next(node for node in ast.parse(path.read_text(encoding="utf-8")).body
                if isinstance(node, ast.FunctionDef) and node.name == "_settings_page_header")
    st = MagicMock()
    scope = {"st": st}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), scope)
    scope["_settings_page_header"]()
    return st.markdown.call_args.args[0]


def test_profile_description_list_has_no_indentation():
    css = profile_css()
    for selector in (".athlete-profile-section dl", ".athlete-profile-row dt", ".athlete-profile-row dd"):
        declarations = css.split(selector + " {", 1)[1].split("}", 1)[0]
        assert "margin: 0;" in declarations
        assert "padding: 0;" in declarations


def test_desktop_compaction_does_not_clip_or_affect_edit_form():
    css = profile_css()
    desktop = css.split("@media (min-width: 1001px)", 1)[1].split("@media (max-width: 1000px)", 1)[0]
    assert ".st-key-settings_profile_summary:has(.athlete-profile-grid) h3" in desktop
    assert "gap: 0.6rem;" in desktop
    assert "padding: 0.1rem 0;" in desktop
    assert "overflow: hidden" not in css
    assert "height:" not in desktop.replace("line-height:", "")
