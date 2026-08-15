from dataclasses import (
    FrozenInstanceError,
)

import pytest

from performancelab.identity import (
    ExternalIdentity,
)


def test_normalizes_external_identity():

    identity = ExternalIdentity(
        issuer=(
            " https://accounts.google.com "
        ),
        subject=" google-subject-123 ",
        email=" Pedro@Example.COM ",
        email_verified=True,
        name=" Pedro Andrade ",
    )

    assert identity.issuer == (
        "https://accounts.google.com"
    )
    assert identity.subject == (
        "google-subject-123"
    )
    assert identity.email == (
        "pedro@example.com"
    )
    assert identity.name == (
        "Pedro Andrade"
    )


def test_provider_key_excludes_email():

    identity = ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-123",
        email="pedro@example.com",
        email_verified=True,
    )

    assert identity.provider_key == (
        "https://accounts.google.com",
        "google-subject-123",
    )


def test_external_identity_is_immutable():

    identity = ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-123",
        email="pedro@example.com",
        email_verified=True,
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        identity.email = (
            "changed@example.com"
        )


def test_empty_name_becomes_none():

    identity = ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-123",
        email="pedro@example.com",
        email_verified=True,
        name=" ",
    )

    assert identity.name is None


@pytest.mark.parametrize(
    (
        "field",
        "value",
        "message",
    ),
    (
        (
            "issuer",
            " ",
            "issuer cannot be empty",
        ),
        (
            "subject",
            " ",
            "subject cannot be empty",
        ),
        (
            "email",
            "invalid-email",
            "email must be valid",
        ),
    ),
)
def test_rejects_invalid_identity_values(
    field,
    value,
    message,
):

    values = {
        "issuer": (
            "https://accounts.google.com"
        ),
        "subject": (
            "google-subject-123"
        ),
        "email": (
            "pedro@example.com"
        ),
        "email_verified": True,
    }

    values[field] = value

    with pytest.raises(
        ValueError,
        match=message,
    ):
        ExternalIdentity(
            **values
        )


def test_unverified_email_remains_factual():

    identity = ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-123",
        email="pedro@example.com",
        email_verified=False,
    )

    assert (
        identity.email_verified
        is False
    )


def test_rejects_non_boolean_verification():

    with pytest.raises(
        TypeError,
        match="must be a boolean",
    ):
        ExternalIdentity(
            issuer=(
                "https://accounts.google.com"
            ),
            subject=(
                "google-subject-123"
            ),
            email=(
                "pedro@example.com"
            ),
            email_verified="yes",
        )