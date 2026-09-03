"""Keep notes layout scoped and preserve editing and card dimensions."""
import ast
from pathlib import Path


SOURCE = (Path(__file__).resolve().parents[1] / "app/components/activities_page.py").read_text(encoding="utf-8")


def test_notes_rows_fit_inside_existing_bottom_slot():
    assert '[data-testid="stVerticalBlock"].st-key-activity_coach_notes' in SOURCE
    assert "grid-template-rows: 28px 184px 34px" in SOURCE
    assert "row-gap: 14px !important" in SOURCE
    assert 28 + 184 + 34 + 2 * 14 == 308 - 34


def test_notes_keep_existing_save_callback_and_textarea_height():
    calls = [n for n in ast.walk(ast.parse(SOURCE)) if isinstance(n, ast.Call)]
    def labelled_call(label):
        return next(n for n in calls if n.args and isinstance(n.args[0], ast.Constant)
                    and n.args[0].value == label)
    notes = labelled_call("Information for the Training Coach")
    assert next(k.value.value for k in notes.keywords if k.arg == "height") == 184
    save = labelled_call("Save information")
    assert next(ast.unparse(k.value) for k in save.keywords if k.arg == "on_click") == "_save_activity_coach_notes"
