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


def test_material_training_changes_invalidate_all_plan_views():
    for name in (
        "regenerate_weekly_plan",
        "import_completed_activities",
        "update_completed_workout",
        "delete_completed_workouts",
    ):
        assert "invalidate_plan_views(" in function_source(name)

    assert "invalidate_daily_brief()" in function_source(
        "confirm_daily_brief_timezone"
    )


def test_restore_and_event_regeneration_invalidate_plan_views():
    assert "invalidate_plan_views(" in function_source(
        "restore_training_plan_revision"
    )
    text = source()
    event_refresh = text.split(
        'pop("event_plan_refresh_requested", False)', 1
    )[1].split("training_coach_permitted", 1)[0]
    assert "invalidate_plan_views(result.athlete.training_plan)" in event_refresh


def test_event_changes_regenerate_the_persistent_plan():
    text = source()
    assert 'pop("event_plan_refresh_requested", False)' in text
    assert 'operation="regenerate_plan_after_event_change"' in text
    assert "GenerateTrainingPlan(" in text
    assert '"Events and training plan updated."' in text


def test_invalidation_clears_attempt_and_visible_resolution():
    body = function_source("invalidate_daily_brief")
    assert 'pop("daily_brief_attempt_key", None)' in body
    assert 'pop("daily_brief_resolution", None)' in body


def test_plan_view_invalidation_clears_drafts_and_tracks_revision():
    body = function_source("invalidate_plan_views")
    assert "invalidate_daily_brief()" in body
    assert '"plan_builder_draft:"' in body
    assert '"plan_view_revision"' in body
    assert "active_revision_id" in body


def test_attempt_key_uses_authenticated_user_and_local_calendar_day():
    text = source()
    assert "ZoneInfo(timezone_preference.timezone_name)" in text
    assert 'f"{current_user.user_id}:{local_day.isoformat()}"' in text
    assert 'st.session_state.get("daily_brief_attempt_key") != daily_brief_attempt_key' in text
