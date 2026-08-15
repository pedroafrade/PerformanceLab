import pytest

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)


def invitation(
    *,
    email="pedro@example.com",
    invitation_id="invitation-1",
):

    return AlphaInvitation(
        invitation_id=invitation_id,
        email=email,
        role="athlete",
        athlete_id="athlete-123",
    )


def test_normalizes_invitation_email():

    alpha_invitation = (
        AlphaInvitation(
            email=" Pedro@Example.COM ",
            role="athlete",
            athlete_id=" athlete-123 ",
        )
    )

    assert alpha_invitation.email == (
        "pedro@example.com"
    )

    assert (
        alpha_invitation.athlete_id
        == "athlete-123"
    )


def test_athlete_invitation_requires_athlete():

    with pytest.raises(
        ValueError,
        match="must have an athlete_id",
    ):
        AlphaInvitation(
            email="pedro@example.com",
            role="athlete",
        )


def test_claims_invitation_immutably():

    original = invitation()

    claimed = original.claim(
        "user-123"
    )

    assert original.is_claimed is False
    assert claimed.is_claimed is True

    assert (
        claimed.claimed_by_user_id
        == "user-123"
    )


def test_cannot_claim_for_another_user():

    claimed = invitation().claim(
        "user-123"
    )

    with pytest.raises(
        ValueError,
        match="already been claimed",
    ):
        claimed.claim(
            "user-456"
        )


def test_repeated_claim_for_same_user_is_idempotent():

    claimed = invitation().claim(
        "user-123"
    )

    assert (
        claimed.claim(
            "user-123"
        )
        is claimed
    )


def test_repository_round_trip(
    tmp_path,
):

    repository = (
        JsonAlphaInvitationRepository(
            tmp_path
        )
    )

    original = invitation()

    repository.save(
        original
    )

    loaded = repository.get(
        original.invitation_id
    )

    assert loaded == original

    assert (
        repository.get_by_email(
            "PEDRO@EXAMPLE.COM"
        )
        == original
    )


def test_repository_updates_claimed_invitation(
    tmp_path,
):

    repository = (
        JsonAlphaInvitationRepository(
            tmp_path
        )
    )

    original = invitation()

    repository.save(
        original
    )

    claimed = original.claim(
        "user-123"
    )

    repository.save(
        claimed
    )

    loaded = repository.get(
        original.invitation_id
    )

    assert loaded.is_claimed is True

    assert (
        loaded.claimed_by_user_id
        == "user-123"
    )


def test_email_can_have_only_one_invitation(
    tmp_path,
):

    repository = (
        JsonAlphaInvitationRepository(
            tmp_path
        )
    )

    repository.save(
        invitation(
            invitation_id="invitation-1"
        )
    )

    with pytest.raises(
        ValueError,
        match="already exists",
    ):
        repository.save(
            invitation(
                invitation_id=(
                    "invitation-2"
                )
            )
        )


def test_delete_removes_invitation(
    tmp_path,
):

    repository = (
        JsonAlphaInvitationRepository(
            tmp_path
        )
    )

    original = invitation()

    repository.save(
        original
    )

    repository.delete(
        original.invitation_id
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get(
            original.invitation_id
        )


def test_unknown_email_raises(
    tmp_path,
):

    repository = (
        JsonAlphaInvitationRepository(
            tmp_path
        )
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get_by_email(
            "unknown@example.com"
        )