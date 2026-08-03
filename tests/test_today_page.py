"""
Tests for the Today page.
"""

from app.components.today_page import (
    show_today_page,
)


def test_show_today_page_exists():

    assert callable(
        show_today_page
    )