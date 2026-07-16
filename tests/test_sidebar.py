"""
Tests for sidebar component.
"""

from app.components.sidebar import (
    show_sidebar,
)


def test_show_sidebar_exists():

    assert callable(
        show_sidebar
    )