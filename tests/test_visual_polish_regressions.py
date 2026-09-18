"""Regression checks for cross-page visual alignment refinements."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "app" / "components"


def source(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_plan_builder_locks_outer_page_and_typical_week_fits_without_scroll():
    text = source("plan_page.py")
    assert 'body:has(div[data-testid="stDialog"] [role="dialog"])' in text
    assert '[data-testid="stAppViewContainer"]:has(' in text
    assert "height: 100dvh !important" in text
    assert ".typical-week-scroll{overflow:hidden" in text
    assert ".typical-week-slot{min-height:1.55rem" in text
    assert "end_hour = max(20" in text


def test_typical_week_header_uses_theme_colours():
    text = source("plan_page.py")
    assert "background:var(--secondary-background-color)" in text
    assert "color:var(--text-color)" in text
    header_styles = text[text.index(".typical-week-corner"):text.index(".typical-week-time")]
    assert "var(--background-color,#fff)" not in header_styles


def test_today_rows_keep_a_plan_like_vertical_gap():
    text = source("today_page.py")
    assert ".st-key-today_brief_recovery_row" in text
    assert "margin-top: 0.75rem" in text
    assert "margin-bottom: 0.75rem" in text
    assert ".st-key-today_guidance_column" in text


def test_recovery_log_management_does_not_expand_the_today_card():
    text = source("today_page.py")
    app = (ROOT.parent / "app.py").read_text(encoding="utf-8")
    assert '@st.dialog("Recovery log", width="small")' in text
    assert "recovery-log-entries" in text
    assert "recovery-log-add-entry" in text
    assert "on_update(RecoveryLogEntry(" in text
    assert "st.rerun()" in text
    assert "def update_recovery_log_entry(entry)" in app
    assert "on_update_recovery_entry=update_recovery_log_entry" in app


def test_recovery_log_shows_recent_entries_inside_a_stable_scroll_area():
    text = source("today_page.py")
    assert 'class="recovery-log-entries"' in text
    assert 'class="recovery-log-entry"' in text
    assert "height: 10.25rem" in text
    assert "max-height: 6.5rem" in text
    assert "overflow-y: auto" in text
    card = text[text.index("def _show_recovery_log("):text.index("def _today_completed_workout(")]
    assert "Private history for awareness only" not in card


def test_today_uses_the_dashboard_spacing_scale():
    text = source("today_page.py")
    dashboard = source("dashboard/dashboard_view.py")
    assert ".st-key-dashboard_page {gap: 0.75rem;}" in dashboard
    assert "gap: 0.75rem" in text
    assert text.count('gap="small"') >= 3


def test_session_equivalents_are_rendered_as_internal_cards():
    text = source("today_page.py")
    assert 'class="today-equivalent-cards"' in text
    assert text.count('class="today-equivalent-card"') == 2
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in text


def test_development_charts_align_and_do_not_render_a_duplicate_zero_axis():
    text = source("development_page.py")
    assert 'padding={"right": 0 if mobile else 48}' in text
    assert 'alt.Y("y:Q", axis=None)' in text
    assert "margin-bottom: -1.9rem" in text


def test_settings_places_escaped_athlete_name_in_the_profile_heading():
    text = source("settings_page.py")
    assert 'class="settings-profile-heading"' in text
    assert 'escape(getattr(athlete, "name", None) or "Unnamed athlete")' in text
    assert '[data-testid="stHeadingWithActionElements"]' in text


def test_plan_and_settings_typography_is_scoped_to_each_page():
    plan = source("plan_page.py")
    settings = source("settings_page.py")
    assert 'section[data-testid="stMain"]:has(.plan-page-header)' in plan
    assert 'section[data-testid="stMain"]:has(.settings-page-header)' in settings
