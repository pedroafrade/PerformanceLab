"""
Tests for sidebar component.
"""

from inspect import (
    signature,
)

from app.components.sidebar import (
    _NAVIGATION_ITEMS,
    _show_navigation,
    _show_user_account,
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
        "today",
        "training",
        "activities",
        "calendar",
        "development",
        "guide",
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
        "nav.guide",
        "nav.settings",
    )


def test_private_alpha_navigation_has_no_user_role():

    parameters = signature(
        _show_navigation
    ).parameters

    assert tuple(
        parameters
    ) == ()


def test_private_alpha_account_uses_athlete_only():

    parameters = signature(
        _show_user_account
    ).parameters

    assert tuple(
        parameters
    ) == (
        "athlete",
        "on_logout",
    )


def test_sidebar_has_no_current_user_parameter():

    parameters = signature(
        show_sidebar
    ).parameters

    assert (
        "current_user"
        not in parameters
    )