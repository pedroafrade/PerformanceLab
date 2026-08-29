"""
Tests for the athlete Settings page.
"""

import inspect

from app.components.athlete_panel import (
    show_athlete_panel,
)
from app.components.settings_page import (
    show_settings_page,
)


def test_show_settings_page_exists():

    assert callable(
        show_settings_page
    )


def test_athlete_panel_supports_hidden_heading():

    signature = inspect.signature(
        show_athlete_panel
    )

    parameter = signature.parameters[
        "show_heading"
    ]

    assert parameter.default is True
    assert (
        parameter.kind
        is inspect.Parameter.KEYWORD_ONLY
    )

def test_settings_supports_training_coach_consent():

    signature = inspect.signature(
        show_settings_page
    )

    assert (
        "training_coach_permitted"
        in signature.parameters
    )

    assert (
        "on_allow_training_coach"
        in signature.parameters
    )

    assert (
        "on_withdraw_training_coach"
        in signature.parameters
    )

def test_settings_supports_visible_support_contact():

    signature = inspect.signature(
        show_settings_page
    )

    assert (
        "support_contact_email"
        in signature.parameters
    )