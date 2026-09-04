"""Native card heights and larger week controls."""
import ast
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1] / "app/components/dashboard"


@pytest.mark.parametrize("key,height", [
    ("dashboard_top_latest", 320), ("dashboard_top_plan", 320),
    ("dashboard_top_event", 320), ("dashboard_current_state", 440),
    ("dashboard_brief", 440), ("dashboard_next_workout", 440), ("dashboard_summary", 440),
    ("another_card", None),
])
def test_border_container_receives_uniform_native_height(key, height):
    tree = ast.parse((ROOT / "widget.py").read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "dashboard_widget")
    future = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    module = ast.fix_missing_locations(ast.Module(body=[future, function], type_ignores=[]))
    st = MagicMock()
    scope = {"st": st, "contextmanager": contextmanager}
    exec(compile(module, "widget.py", "exec"), scope)
    with scope["dashboard_widget"](key=key):
        pass
    assert st.container.call_args.kwargs.get("height") == height
    assert st.container.call_args.kwargs["border"] is True


def test_navigation_uses_matching_side_tracks_and_double_size():
    source = (ROOT / "cards/planning_card.py").read_text(encoding="utf-8")
    assert "st.columns([0.45, 7, 0.45], gap=None)[1]" in source
    assert "day_columns = columns[1:-1]" in source
    assert "height: 50px" in source
    assert "font-size: 2.7rem" in source
    assert "previous_column, next_column = st.columns(2" not in source
