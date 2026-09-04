import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "app/app.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def handled_operations():
    operations = set()
    for handler in (
        node for node in ast.walk(TREE) if isinstance(node, ast.ExceptHandler)
    ):
        for call in (
            node for node in ast.walk(handler)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "capture_exception"
        ):
            for keyword in call.keywords:
                if keyword.arg == "operation" and isinstance(keyword.value, ast.Constant):
                    operations.add(keyword.value.value)
    return operations


def test_daily_brief_failures_are_reported_without_stopping_the_app():
    assert {
        "daily_brief_timezone_lookup",
        "daily_brief_local_day",
        "daily_brief_resolution",
    } <= handled_operations()


def test_daily_brief_failure_paths_do_not_show_raw_errors_or_stop_streamlit():
    start = SOURCE.index("daily_brief_resolution = st.session_state.get")
    end = SOURCE.index("should_save_athlete =", start)
    segment = SOURCE[start:end]
    assert "st.error(" not in segment
    assert "st.exception(" not in segment
    assert "st.stop(" not in segment
    assert "daily_brief_resolution = None" in segment
