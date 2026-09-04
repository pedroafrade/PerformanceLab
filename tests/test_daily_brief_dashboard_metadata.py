from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import ast


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "app/components/dashboard/dashboard_view.py"


def metadata_helper():
    source = SOURCE_PATH.read_text(encoding="utf-8")
    node = next(
        item for item in ast.parse(source).body
        if isinstance(item, ast.FunctionDef) and item.name == "_daily_brief_metadata"
    )
    namespace = {"datetime": datetime, "timezone": timezone}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(SOURCE_PATH), "exec"), namespace)
    return namespace["_daily_brief_metadata"]


def test_generated_metadata_is_human_readable_and_utc_explicit():
    value = metadata_helper()(SimpleNamespace(
        status="generated",
        generated_at="2026-09-04T10:15:00+00:00",
        reason="daily_or_context_refresh",
    ))
    assert value == "Updated 04 Sep 2026 · 10:15 UTC · Daily or context refresh"


def test_cached_result_is_identified_as_reused():
    value = metadata_helper()(SimpleNamespace(
        status="cached",
        generated_at="2026-09-04T10:15:00Z",
        reason="daily_or_context_refresh",
    ))
    assert value.startswith("Reused 04 Sep 2026")


def test_missing_or_invalid_metadata_is_not_exposed():
    helper = metadata_helper()
    assert helper(None) is None
    assert helper(SimpleNamespace(generated_at="provider error payload")) is None


def test_dashboard_labels_local_guidance_as_fallback():
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert "Local guidance from Today · Fallback" in source
