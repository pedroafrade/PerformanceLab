"""Create an email-only invitation for the private alpha."""

from __future__ import annotations

import argparse
import os

from performancelab.alpha_invitation import AlphaInvitation
from performancelab.runtime_configuration import RuntimeConfiguration
from performancelab.storage.repository_factory import build_repository_bundle


def invite_alpha_user(email: str, invitation_repository) -> AlphaInvitation:
    """Create an unclaimed athlete invitation, idempotently."""

    normalized_email = email.strip().lower()
    try:
        existing = invitation_repository.get_by_email(normalized_email)
    except KeyError:
        invitation = AlphaInvitation(email=normalized_email)
        invitation_repository.save(invitation)
        return invitation

    if existing.is_claimed:
        raise ValueError("This invitation has already been claimed.")

    return existing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Invite one athlete to the Journal private alpha."
    )
    parser.add_argument("email", help="Verified Google account email")
    args = parser.parse_args(argv)

    configuration = RuntimeConfiguration.from_mapping(dict(os.environ))
    if not configuration.uses_postgresql:
        raise RuntimeError("Alpha invitations require PostgreSQL persistence.")

    repositories = build_repository_bundle(configuration)
    try:
        with repositories.transaction():
            invitation = invite_alpha_user(
                args.email,
                repositories.alpha_invitation_repository,
            )
        print(f"Invitation ready for {invitation.email}.")
    finally:
        repositories.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
