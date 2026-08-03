"""
Tests for sidebar component.
"""

from app.components.sidebar import (
    _NAVIGATION_ITEMS,
    show_sidebar,
)


def test_show_sidebar_exists():

    assert callable(
        show_sidebar
    )


def test_sidebar_uses_public_page_navigation():

    routes = tuple(
        page
        for page, _, _ in _NAVIGATION_ITEMS
    )

    assert routes == (
        "dashboard",
        "training",
        "activities",
        "calendar",
        "development",
        "settings",
    )


def test_sidebar_uses_semantic_translation_keys():

    translation_keys = tuple(
        label_key
        for _, label_key, _ in _NAVIGATION_ITEMS
    )

    assert translation_keys == (
        "nav.today",
        "nav.plan",
        "nav.activities",
        "nav.calendar",
        "nav.development",
        "nav.settings",
    )