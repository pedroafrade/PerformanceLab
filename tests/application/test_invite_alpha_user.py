import pytest

from performancelab.application.invite_alpha_user import (
    invite_alpha_user,
    list_alpha_invitations,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)


def test_creates_email_only_invitation(tmp_path):
    repository = JsonAlphaInvitationRepository(tmp_path)

    invitation = invite_alpha_user(
        " Friend@Example.com ",
        repository,
    )

    assert invitation.email == "friend@example.com"
    assert invitation.athlete_id is None
    assert invitation.is_claimed is False


def test_reuses_existing_unclaimed_invitation(tmp_path):
    repository = JsonAlphaInvitationRepository(tmp_path)
    first = invite_alpha_user("friend@example.com", repository)
    second = invite_alpha_user("friend@example.com", repository)
    assert second == first


def test_rejects_claimed_invitation(tmp_path):
    repository = JsonAlphaInvitationRepository(tmp_path)
    invitation = invite_alpha_user("friend@example.com", repository)
    repository.save(invitation.claim("user-1"))

    with pytest.raises(ValueError, match="already been claimed"):
        invite_alpha_user("friend@example.com", repository)


def test_lists_invitations_by_email_with_claim_state(tmp_path):
    repository = JsonAlphaInvitationRepository(tmp_path)

    second = invite_alpha_user("zeta@example.com", repository)
    first = invite_alpha_user("alpha@example.com", repository)
    repository.save(second.claim("user-1"))

    invitations = list_alpha_invitations(repository)

    assert [item.email for item in invitations] == [
        "alpha@example.com",
        "zeta@example.com",
    ]
    assert invitations[0] == first
    assert invitations[0].is_claimed is False
    assert invitations[1].is_claimed is True
