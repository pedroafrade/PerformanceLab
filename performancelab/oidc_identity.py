"""
PerformanceLab

Conversion of factual OIDC claims into a domain identity.
"""

from collections.abc import (
    Mapping,
)

from performancelab.identity import (
    ExternalIdentity,
)


def external_identity_from_claims(
    claims: Mapping[
        str,
        object,
    ],
) -> ExternalIdentity:
    """
    Build an external identity from verified OIDC claims.

    Streamlit and the configured OIDC provider remain
    responsible for validating the identity token.
    """

    if not isinstance(
        claims,
        Mapping,
    ):
        raise TypeError(
            "OIDC claims must be a mapping."
        )

    required_claims = (
        "iss",
        "sub",
        "email",
        "email_verified",
    )

    missing_claims = [
        claim
        for claim in required_claims
        if claim not in claims
    ]

    if missing_claims:

        missing = ", ".join(
            missing_claims
        )

        raise ValueError(
            "Missing required OIDC claims: "
            f"{missing}."
        )

    name = claims.get(
        "name"
    )

    return ExternalIdentity(
        issuer=claims["iss"],
        subject=claims["sub"],
        email=claims["email"],
        email_verified=(
            claims["email_verified"]
        ),
        name=name,
    )