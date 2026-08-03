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