"""Regression coverage for the Journal application identity."""

from pathlib import Path

from app.components.brand import journal_logo_html


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

    html = journal_logo_html(placement="login")
    assert "Journal — Adaptive Endurance Training" in html
    assert "prefers-color-scheme: dark" in html
    assert html.count("data:image/png;base64,") == 2


def test_browser_title_uses_journal_name_and_icon():
    source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
    assert 'page_title="Journal — Adaptive Endurance Training"' in source
    assert 'journal_logo_html(\n                placement="login"' in source
    assert 'journal-icon-512x512_black.png' in source
