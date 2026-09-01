"""Isolated rendering and safety regressions for the compact UI."""
import ast
from datetime import date
from html import escape
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest

COMPONENTS = Path(__file__).resolve().parents[1] / "app" / "components"

def source(filename):
    return (COMPONENTS / filename).read_text(encoding="utf-8")

def helper(filename, name, **namespace):
    node = next(n for n in ast.parse(source(filename)).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    scope = {"date": date, "escape": escape, **namespace}
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, "exec"), scope)
    return scope[name]

def test_calendar_navigation_precedes_selected_day_in_right_column():
    tree = ast.parse(source("calendar_page.py"))
    column = next(n for n in ast.walk(tree) if isinstance(n, ast.With)
                  and any(isinstance(i.context_expr, ast.Name)
                          and i.context_expr.id == "sidebar_column" for i in n.items))
    calls = {n.func.id: n.lineno for n in ast.walk(column)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert calls["_show_month_navigation"] < calls["_show_selected_day"] < calls["_show_upcoming_events"]
    assert "_calendar_html" not in calls

def test_sidebar_identity_has_no_action_buttons():
    st = MagicMock()
    helper("sidebar.py", "_show_user_account", st=st)(
        SimpleNamespace(name="<Athlete>"), MagicMock())
    st.button.assert_not_called()
    assert "&lt;Athlete&gt;" in st.markdown.call_args.args[0]

@pytest.mark.parametrize("clicked", [False, True])
def test_logout_callback_requires_click(clicked):
    st = MagicMock()
    st.button.return_value = clicked
    callback = MagicMock()
    helper("sidebar.py", "_show_sidebar_logout", st=st)(callback)
    assert callback.call_count == int(clicked)
    st.divider.assert_called_once()
    assert st.button.call_args.kwargs["key"] == "sidebar_logout"

def test_logout_follows_import_without_import_label():
    text = source("sidebar.py")
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "show_sidebar")
    calls = {n.func.id: n.lineno for n in ast.walk(node)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert calls["show_activity_input"] < calls["_show_sidebar_logout"]
    assert "sidebar-section-label" not in ast.get_source_segment(text, node)
    assert "sidebar_edit_athlete" not in text

def settings_harness():
    st = MagicMock()
    st.tabs.return_value = [MagicMock() for _ in range(4)]
    st.columns.return_value = [MagicMock(), MagicMock()]
    athlete = object()
    profile = MagicMock(return_value=athlete)
    coach = MagicMock()
    st.attach_mock(profile, "profile_render")
    st.attach_mock(coach, "coach_render")
    confirmed = helper("settings_page.py", "participant_deletion_confirmed",
                       PARTICIPANT_DELETION_PHRASE="DELETE MY DATA")
    show = helper("settings_page.py", "show_settings_page", st=st,
                  _settings_page_header=MagicMock(), show_athlete_panel=profile,
                  show_training_coach_consent_settings=coach,
                  participant_deletion_confirmed=confirmed,
                  privacy_contact_mailto=lambda v: "mailto:" + v,
                  support_contact_mailto=lambda v: "mailto:" + v)
    return st, athlete, show

def test_settings_profile_first_and_export_preserved():
    st, athlete, show = settings_harness()
    st.checkbox.return_value = False
    st.text_input.return_value = ""
    assert show(athlete, participant_export_json='{"example":true}') is athlete
    st.profile_render.assert_called_once_with(
        athlete, show_heading=False, compact_summary=True)
    calls = [c[0] for c in st.mock_calls]
    assert calls.index("profile_render") < calls.index("tabs") < calls.index("coach_render")
    assert st.download_button.call_args.kwargs["data"] == '{"example":true}'

@pytest.mark.parametrize("ack,phrase,enabled", [
    (False, "DELETE MY DATA", False), (True, "", False),
    (True, "delete my data", False), (True, "DELETE MY DATA", True),
])
def test_deletion_confirmations_preserved(ack, phrase, enabled):
    st, athlete, show = settings_harness()
    st.checkbox.return_value = ack
    st.text_input.return_value = phrase
    callback = MagicMock()
    show(athlete, on_delete_participant_data=callback)
    assert st.button.call_args.kwargs["disabled"] is (not enabled)
    assert st.button.call_args.kwargs["on_click"] is callback
    callback.assert_not_called()

def test_guidance_preserves_and_escapes_text():
    render = helper("today_page.py", "_guidance_item_html")
    text = render(index=7, text="<script>long text</script>")
    assert "&lt;script&gt;long text&lt;/script&gt;" in text
    assert "today-guidance-text" in text
    assert "7" in text

def test_today_alignment_is_desktop_only_without_clipping():
    st = MagicMock()
    helper("today_page.py", "_apply_today_page_styles", st=st)("Today")
    css = st.markdown.call_args.args[0]
    for value in ("@media (min-width: 761px)", "margin-top: auto;",
                  "today_session_card", "today_adaptation_card", "line-height: 1.25;"):
        assert value in css
    assert "overflow: hidden" not in css
    assert "position: fixed" not in css

def test_compact_profile_is_opt_in_and_form_preserved():
    text = source("athlete_panel.py")
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "show_athlete_panel")
    defaults = dict(zip([a.arg for a in node.args.kwonlyargs], node.args.kw_defaults))
    assert ast.literal_eval(defaults["compact_summary"]) is False
    assert "_show_athlete_form" in ast.get_source_segment(text, node)

def test_guidance_heading_and_body_are_one_flow():
    st = MagicMock()
    row = helper("today_page.py", "_guidance_item_html")
    helper("today_page.py", "_show_guidance_card", st=st, _guidance_item_html=row)(
        title="Why <today>", items=("First & second",))
    html = st.html.call_args.args[0]
    assert html.index("Why &lt;today&gt;") < html.index("First &amp; second")
    st.markdown.assert_not_called()

@pytest.mark.parametrize("with_zones", [False, True])
def test_compact_profile_preserves_values_and_escapes(with_zones):
    profile = SimpleNamespace(uses_manual_zones=True, zones=[
        SimpleNamespace(name="<Z1>", lower_bpm=100, upper_bpm=120)]) if with_zones else None
    nutrition = SimpleNamespace(carbohydrate_per_hour=80, fluid_lower_ml_per_hour=450,
        fluid_upper_ml_per_hour=600, sodium_lower_mg_per_hour=400,
        sodium_upper_mg_per_hour=600, gel_carbohydrate_grams=25,
        pre_race_carbohydrate_lower=60, pre_race_carbohydrate_upper=80,
        source="athlete-tested")
    athlete = SimpleNamespace(birth_date=None, gender="<test>", height=1.78,
        weight=74, ftp=220, max_hr=205, resting_hr=65, threshold_hr=177,
        analytics=SimpleNamespace(heart_rate_profile=profile), nutrition_profile=nutrition)
    render = helper("athlete_panel.py", "_compact_profile_html",
                    _display_value=lambda value, unit="": str(value) + unit)
    html = render(athlete)
    assert "&lt;test&gt;" in html and "<test>" not in html
    for value in ("177 bpm", "220 W", "80 g/h", "450–600 ml/h", "athlete tested"):
        assert value in html
    assert html.count('<section ') == 3
    assert ("&lt;Z1&gt;" if with_zones else "Set maximum and resting heart rate") in html

def test_profile_and_guidance_have_readable_spacing():
    css = source("settings_page.py")
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in css
    assert "@media (max-width: 1000px)" in css
    assert "line-height: 1.4" in css
    assert '.st-key-settings_profile_summary p' not in css
    today = source("today_page.py")
    assert 'margin: 0 0 0.6rem' in today
    assert 'margin: 0 0 0.65rem' in today

def test_calendar_alignment_is_scoped_to_desktop():
    text = source("calendar_page.py")
    css = text.split("@media (min-width: 901px)", 1)[1].split("@media (max-width: 900px)", 1)[0]
    assert "calendar_events_card" in css and "calendar_grid_area" in css
    assert "flex: 1 0 auto" in css
    assert "position: absolute" not in css
