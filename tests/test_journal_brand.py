"""Regression coverage for the Journal application identity."""

from pathlib import Path

from app.components.brand import (
    journal_logo_html,
    journal_sidebar_button_css,
)


ROOT = Path(__file__).resolve().parents[1]


def test_journal_assets_are_bundled_and_rendered_for_both_themes():
    assets = ROOT / "app" / "assets"
    for filename in (
        "journal-logo-black-1600x400.png",
        "journal-logo-white-1600x400.png",
        "journal-icon-512x512_black.png",
        "journal-icon-512x512_white.png",
    ):
        assert (assets / filename).is_file()

    light_html = journal_logo_html(placement="login", theme="light")
    dark_html = journal_logo_html(placement="login", theme="dark")
    assert "Journal — Adaptive Endurance Training" in light_html
    assert light_html.count("data:image/png;base64,") == 1
    assert dark_html.count("data:image/png;base64,") == 1
    assert light_html != dark_html

    button_css = journal_sidebar_button_css(theme="dark")
    assert ".st-key-sidebar_brand button" in button_css
    assert 'background-image: url("data:image/png;base64,' in button_css


def test_browser_title_uses_journal_name_and_icon():
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert 'page_title="Journal — Adaptive Endurance Training"' in source
    assert 'journal_logo_html(\n                placement="login"' in source
    assert "theme=st.context.theme.type" in source
    assert 'journal-icon-512x512_black.png' in source


def test_login_screen_offers_google_and_email_code():
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

    assert '"Sign in with Google"' in source
    assert 'args=("google",)' in source
    assert '"Continue with email code"' in source
    assert 'args=("email",)' in source


def test_sidebar_logo_remains_a_dashboard_button():
    source = (
        ROOT / "app" / "components" / "sidebar.py"
    ).read_text(encoding="utf-8")

    assert '"Journal home"' in source
    assert 'key="sidebar_brand"' in source
    assert 'args=(_HOME_PAGE,)' in source
