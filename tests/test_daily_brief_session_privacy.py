import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app/app.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def function_source(name):
    node = next(
        item for item in TREE.body
        if isinstance(item, ast.FunctionDef) and item.name == name
    )
    return ast.get_source_segment(SOURCE, node)


def test_withdrawing_consent_removes_daily_brief_from_session():
    body = function_source("withdraw_training_coach")
    assert "training_coach_consent_manager.withdraw(" in body
    assert "invalidate_daily_brief()" in body


def test_granting_consent_allows_a_fresh_resolution():
    body = function_source("allow_training_coach")
    assert "training_coach_consent_manager.grant(" in body
    assert "invalidate_daily_brief()" in body


def test_logout_clears_comment_attempt_and_timezone_widget_state():
    body = function_source("logout")
    assert "invalidate_daily_brief()" in body
    assert '"daily_brief_timezone_selection"' in body


def test_invalidation_removes_both_sensitive_session_values():
    body = function_source("invalidate_daily_brief")
    assert 'pop("daily_brief_attempt_key", None)' in body
    assert 'pop("daily_brief_resolution", None)' in body
