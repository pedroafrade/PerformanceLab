import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app/app.py"


def source():
    return APP.read_text(encoding="utf-8")


def function_source(name):
    text = source()
    node = next(
        item for item in ast.parse(text).body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    return ast.get_source_segment(text, node)


def test_material_training_changes_invalidate_daily_brief():
    for name in (
        "regenerate_weekly_plan",
        "import_completed_activities",
        "update_completed_workout",
        "delete_completed_workouts",
        "confirm_daily_brief_timezone",
    ):
        assert "invalidate_daily_brief()" in function_source(name)


def test_invalidation_clears_attempt_and_visible_resolution():
    body = function_source("invalidate_daily_brief")
    assert 'pop("daily_brief_attempt_key", None)' in body
    assert 'pop("daily_brief_resolution", None)' in body


def test_attempt_key_uses_authenticated_user_and_local_calendar_day():
    text = source()
    assert "ZoneInfo(timezone_preference.timezone_name)" in text
    assert 'f"{current_user.user_id}:{local_day.isoformat()}"' in text
    assert 'st.session_state.get("daily_brief_attempt_key") != daily_brief_attempt_key' in text
