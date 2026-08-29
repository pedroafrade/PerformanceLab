"""
Tests for the participant-facing support contact.
"""

import inspect

import pytest

from app.components.settings_page import (
    show_settings_page,
    support_contact_mailto,
)


def test_builds_support_contact_mail_link():

    assert support_contact_mailto(
        "Support@Example.COM"
    ) == (
        "mailto:support@example.com"
    )


def test_rejects_missing_support_contact():

    with pytest.raises(
        ValueError,
        match="valid support contact",
    ):

        support_contact_mailto(
            ""
        )


def test_rejects_invalid_support_contact():

    with pytest.raises(
        ValueError,
        match="valid support contact",
    ):

        support_contact_mailto(
            "not-an-email"
        )


def test_settings_page_accepts_support_contact():

    signature = inspect.signature(
        show_settings_page
    )

    parameter = signature.parameters[
        "support_contact_email"
    ]

    assert parameter.default is None
    assert (
        parameter.kind
        is inspect.Parameter.KEYWORD_ONLY
    )