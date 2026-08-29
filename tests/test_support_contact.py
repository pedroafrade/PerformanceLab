"""
Tests for the participant-facing support contact.
"""

import inspect

from pathlib import (
    Path,
)

import pytest

from app.components.settings_page import (
    show_settings_page,
    support_contact_mailto,
)

APP_PATH = (
    Path(__file__).parents[1]
    / "app"
    / "app.py"
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

def test_invitation_rejection_shows_support_contact():

    source = APP_PATH.read_text(
        encoding="utf-8"
    )

    normalized_source = " ".join(
        source.split()
    )

    rejection_block = (
        normalized_source
        .split(
            "except PermissionError as error:",
            1,
        )[1]
        .split(
            "except ( TypeError,",
            1,
        )[0]
    )

    assert (
        '"Access to this private alpha "'
        in rejection_block
    )
    assert (
        '"requires an invitation."'
        in rejection_block
    )
    assert (
        "runtime_configuration "
        ".support_contact_email"
        in rejection_block
    )
    assert (
        '"Support contact: "'
        in rejection_block
    )
    assert (
        "f\"(mailto:{support_contact_email})\""
        in rejection_block
    )
    assert '"Sign out"' in rejection_block

    assert (
        rejection_block.index(
            '"Support contact: "'
        )
        < rejection_block.index(
            '"Sign out"'
        )
    )