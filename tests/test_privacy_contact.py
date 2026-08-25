"""
Tests for the participant-facing privacy contact.
"""

import pytest

from app.components.settings_page import (
    privacy_contact_mailto,
)


def test_builds_privacy_contact_mail_link():

    assert privacy_contact_mailto(
        "Privacy@Example.COM"
    ) == (
        "mailto:privacy@example.com"
    )


def test_rejects_missing_privacy_contact():

    with pytest.raises(
        ValueError,
        match="valid privacy contact",
    ):

        privacy_contact_mailto(
            ""
        )


def test_rejects_invalid_privacy_contact():

    with pytest.raises(
        ValueError,
        match="valid privacy contact",
    ):

        privacy_contact_mailto(
            "not-an-email"
        )