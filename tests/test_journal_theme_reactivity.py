"""Regression coverage for client-side Journal theme changes."""

from app.components.brand import (
    journal_logo_html,
    journal_sidebar_button_css,
)


def test_login_logo_reacts_without_a_streamlit_rerun():
    light_html = journal_logo_html(
        placement="login",
        theme="light",
    )
    dark_html = journal_logo_html(
        placement="login",
        theme="dark",
    )

    assert "journal-logo-initial-light" in light_html
    assert "journal-logo-initial-dark" in dark_html
    assert '[data-theme="dark"]' in light_html
    assert '[data-theme="light"]' in dark_html
    assert "invert(1) hue-rotate(180deg)" in light_html


def test_sidebar_button_reacts_without_losing_navigation():
    light_css = journal_sidebar_button_css(theme="light")
    dark_css = journal_sidebar_button_css(theme="dark")

    assert '[data-theme="dark"]' in light_css
    assert '[data-theme="light"]' in dark_css
    assert "invert(1) hue-rotate(180deg)" in light_css
    assert ".st-key-sidebar_brand button" in light_css
    assert "width: 15rem !important" in light_css
