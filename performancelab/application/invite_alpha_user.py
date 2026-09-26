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


def list_alpha_invitations(invitation_repository) -> tuple[AlphaInvitation, ...]:
    """Return invitations in a stable, administrator-friendly order."""

    return tuple(
        sorted(
            invitation_repository.list(),
            key=lambda invitation: invitation.email,
        )
    )


def _print_invitation_list(invitation_repository) -> None:
    """Print a compact invitation report for the Cloud Run job."""

    print("EMAIL\tROLE\tSTATUS")
    for invitation in list_alpha_invitations(invitation_repository):
        status = "claimed" if invitation.is_claimed else "unclaimed"
        print(f"{invitation.email}\t{invitation.role}\t{status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manage Journal private alpha invitations."
    )
    parser.add_argument(
        "email",
        nargs="?",
        help="Email address to invite",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_invitations",
        help="List invited email addresses and their status",
    )
    args = parser.parse_args(argv)

    if args.list_invitations and args.email:
        parser.error("email cannot be combined with --list")
    if not args.list_invitations and not args.email:
        parser.error("provide an email address or --list")

    configuration = RuntimeConfiguration.from_mapping(dict(os.environ))
    if not configuration.uses_postgresql:
        raise RuntimeError("Alpha invitations require PostgreSQL persistence.")

    repositories = build_repository_bundle(configuration)
    try:
        if args.list_invitations:
            _print_invitation_list(
                repositories.alpha_invitation_repository
            )
            return 0

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
