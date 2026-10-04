"""Presentation boundaries: ordered phone cards and unchanged PC chart data."""
from pathlib import Path
import re

import pytest
from streamlit.testing.v1 import AppTest

from app.components.i18n import translate
from app.components.mobile_layout import MOBILE_LAYOUT_CSS
from app.components import plan_page
from performancelab import Athlete
from performancelab.presentation import PlanPresenter


@pytest.mark.parametrize("page, keys", [
    ("dashboard_page", ["dashboard_current_state", "dashboard_next_workout", "dashboard_brief",
                        "dashboard_top_plan", "dashboard_top_latest", "dashboard_top_event", "dashboard_summary"]),
    ("today_page", ["today-recommendation-card", "today_session_card", "today_session_equivalent",
                    "today_metrics", "today_recovery_log", "today_guidance_column", "today_analysis"]),
    ("development_page", ["development_analysis", "development_kpi_row", "development_details"]),
])
def test_requested_phone_order_is_scoped_below_desktop_breakpoint(page, keys):
    assert MOBILE_LAYOUT_CSS.strip().startswith("@media (max-width: 700px) {")
    assert MOBILE_LAYOUT_CSS.count("@media") == 1
    for position, key in enumerate(keys, 1):
        assert re.search(rf"\.st-key-{page} \.st-key-{key} \{{order:{position};", MOBILE_LAYOUT_CSS)
    assert "display:contents !important" in MOBILE_LAYOUT_CSS
    # Card content must retain its own layout; only ancestors are flattened.
    assert ":not(" + ",".join(".st-key-" + key for key in keys) + ")" in MOBILE_LAYOUT_CSS


@pytest.mark.parametrize("language, expected", [("en", "Guide"), ("pt", "Guia")])
def test_short_guide_label(language, expected):
    assert translate("nav.guide", language=language) == expected


@pytest.mark.parametrize("module, function", [
    ("dashboard.dashboard_view", "show_dashboard"),
    ("today_page", "show_today_page"),
    ("development_page", "show_development_page"),
    ("plan_page", "show_plan_page"),
])
def test_pages_render_with_real_streamlit_after_mobile_wrappers(module, function):
    script = f'''
import streamlit as st
from datetime import datetime, timedelta
from performancelab import Athlete
from app.components.{module} import {function}
st.set_page_config(layout="wide")
a = Athlete(name="Presentation test")
a.training_plan.schedule(
    scheduled_at=datetime.now() + timedelta(days=1), sport="Running",
    title="Easy Run", duration=timedelta(minutes=45), intensity="Easy", phase="Base",
)
{function}(a)
'''
    app = AppTest.from_string(script, default_timeout=15).run()
    assert not app.exception


@pytest.mark.parametrize("builder", [plan_page._planned_load_chart, plan_page._distance_elevation_chart])
def test_mobile_plan_chart_keeps_full_data_and_desktop_spec(builder, monkeypatch):
    from datetime import datetime, timedelta
    athlete = Athlete(name="Chart test")
    for day in range(70):
        athlete.training_plan.schedule(
            scheduled_at=datetime.now() + timedelta(days=day), sport="Running",
            title="Easy Run", duration=timedelta(minutes=45), intensity="Easy", phase="Base",
        )
    plan = PlanPresenter(plan=athlete.training_plan, history=athlete.history).build(reference_day=datetime.now().date())
    original = builder(plan).to_dict()
    charts = []
    from contextlib import nullcontext
    monkeypatch.setattr(plan_page.st, "html", lambda *args, **kwargs: None)
    monkeypatch.setattr(plan_page.st, "container", lambda **kwargs: nullcontext())
    monkeypatch.setattr(plan_page.st, "altair_chart", lambda chart, **kwargs: charts.append(chart.to_dict()))
    plan_page._show_responsive_plan_chart(plan, builder, key="regression")
    assert charts[0] == original
    assert len(plan.chart_points) == 70
    # Compare all data, layers, domains and transforms, whether data is inline
    # or Altair consolidates it into named datasets.
    assert {k: v for k, v in charts[1].items() if k not in {"height", "width", "config"}} == {
        k: v for k, v in original.items() if k not in {"height", "width", "config"}
    }
    assert charts[1]["height"] == 220
    assert charts[1]["width"] >= 680
    assert charts[1]["config"]["axis"]["labelFontSize"] == 11


def test_infrastructure_keeps_the_concurrency_that_unblocked_mobile_loading():
    text = (Path(__file__).resolve().parents[1] / "infra/google-alpha/main.tf").read_text()
    assert "max_instance_request_concurrency = 20" in text
    assert "max_instance_count = 2" in text
