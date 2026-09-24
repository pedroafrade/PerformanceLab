import pytest

from performancelab.application.invite_alpha_user import invite_alpha_user
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
