import pytest

from performancelab.oidc_identity import (
    external_identity_from_claims,
)


def google_claims():
    """
    Return representative factual Google OIDC claims.
    """

    return {
        "is_logged_in": True,
        "iss": (
            "https://accounts.google.com"
        ),
        "sub": "google-subject-123",
        "email": "Pedro@Example.com",
        "email_verified": True,
        "name": "Pedro Frade",
        "picture": (
            "https://example.com/avatar.png"
        ),
    }


def test_builds_external_identity_from_claims():

    identity = (
        external_identity_from_claims(
            google_claims()
        )
    )

    assert (
        identity.issuer
        == "https://accounts.google.com"
    )

    assert (
        identity.subject
        == "google-subject-123"
    )

    assert (
        identity.email
        == "pedro@example.com"
    )

    assert identity.email_verified is True

    assert (
        identity.name
        == "Pedro Frade"
    )


def test_ignores_unrelated_oidc_claims():

    claims = google_claims()

    claims["aud"] = "client-id"
    claims["nonce"] = "nonce-value"
    claims["exp"] = 1786838400

    identity = (
        external_identity_from_claims(
            claims
        )
    )

    assert (
        identity.subject
        == "google-subject-123"
    )


@pytest.mark.parametrize(
    "missing_claim",
    (
        "iss",
        "sub",
        "email",
        "email_verified",
    ),
)
def test_rejects_missing_required_claim(
    missing_claim,
):

    claims = google_claims()

    del claims[
        missing_claim
    ]

    with pytest.raises(
        ValueError,
        match="Missing required OIDC claims",
    ):
        external_identity_from_claims(
            claims
        )


def test_rejects_unverified_email():

    claims = google_claims()

    claims["email_verified"] = False

    identity = (
        external_identity_from_claims(
            claims
        )
    )

    assert (
        identity.email_verified
        is False
    )


def test_rejects_invalid_claim_collection():

    with pytest.raises(
        TypeError,
        match="must be a mapping",
    ):
        external_identity_from_claims(
            None
        )