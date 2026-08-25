"""
Tests for the strong participant deletion confirmation.
"""

from app.components.settings_page import (
    PARTICIPANT_DELETION_PHRASE,
    participant_deletion_confirmed,
)


def test_requires_exact_deletion_phrase_and_acknowledgement():

    assert participant_deletion_confirmed(
        PARTICIPANT_DELETION_PHRASE,
        acknowledged=True,
    )


def test_refuses_phrase_without_acknowledgement():

    assert not participant_deletion_confirmed(
        PARTICIPANT_DELETION_PHRASE,
        acknowledged=False,
    )


def test_refuses_incorrect_phrase():

    assert not participant_deletion_confirmed(
        "delete my data",
        acknowledged=True,
    )

    assert not participant_deletion_confirmed(
        "DELETE ACCOUNT",
        acknowledged=True,
    )


def test_allows_surrounding_spaces_only():

    assert participant_deletion_confirmed(
        "  DELETE MY DATA  ",
        acknowledged=True,
    )


def test_refuses_non_string_confirmation():

    assert not participant_deletion_confirmed(
        None,
        acknowledged=True,
    )