import pytest

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.application import (
    ProvisionInvitedUser,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.identity import (
    ExternalIdentity,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)
from performancelab.storage.json_athlete_repository import (
    JsonAthleteRepository,
)
from performancelab.storage.json_external_identity_repository import (
    JsonExternalIdentityRepository,
)
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)


def repositories(
    tmp_path,
):

    return {
        "user_repository": (
            JsonUserRepository(
                tmp_path / "users"
            )
        ),
        "identity_repository": (
            JsonExternalIdentityRepository(
                tmp_path / "identities"
            )
        ),
        "invitation_repository": (
            JsonAlphaInvitationRepository(
                tmp_path / "invitations"
            )
        ),
        "access_repository": (
            JsonAthleteAccessRepository(
                tmp_path / "access"
            )
        ),
        "athlete_repository": (
            JsonAthleteRepository(
                tmp_path / "athletes"
            )
        ),
    }


def external_identity(
    *,
    email=(
        "pedro@example.com"
    ),
    verified=True,
):

    return ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-123",
        email=email,
        email_verified=verified,
        name="Pedro",
    )


def prepare_invitation(
    repository_set,
):

    athlete = Athlete(
        name="Pedro"
    )

    repository_set[
        "athlete_repository"
    ].save(
        athlete
    )

    invitation = AlphaInvitation(
        invitation_id="invitation-1",
        email="pedro@example.com",
        role="athlete",
        athlete_id=athlete.athlete_id,
    )

    repository_set[
        "invitation_repository"
    ].save(
        invitation
    )

    return athlete, invitation


def prepare_email_only_invitation(
    repository_set,
):
    invitation = AlphaInvitation(
        invitation_id="invitation-email-only",
        email="pedro@example.com",
        role="athlete",
    )
    repository_set[
        "invitation_repository"
    ].save(invitation)
    return invitation


def test_first_login_creates_athlete_for_email_only_invitation(
    tmp_path,
):
    repository_set = repositories(tmp_path)
    invitation = prepare_email_only_invitation(
        repository_set
    )

    result = ProvisionInvitedUser(
        **repository_set
    ).execute(external_identity())

    assert result.created is True
    assert result.user.athlete_id is not None
    athlete = repository_set[
        "athlete_repository"
    ].get(result.user.athlete_id)
    assert athlete.onboarding_completed is False
    assert athlete.onboarding_step == 1
    assert athlete.name == "Pedro"
    assert result.access_grant.athlete_id == athlete.athlete_id
    assert result.invitation.athlete_id == athlete.athlete_id
    assert result.invitation.is_claimed is True

    stored = repository_set[
        "invitation_repository"
    ].get(invitation.invitation_id)
    assert stored.athlete_id == athlete.athlete_id
    assert stored.claimed_by_user_id == result.user.user_id


def test_provisions_verified_invited_user(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    athlete, invitation = (
        prepare_invitation(
            repository_set
        )
    )

    result = ProvisionInvitedUser(
        **repository_set
    ).execute(
        external_identity()
    )

    assert result.created is True
    assert (
        result.user.email
        == "pedro@example.com"
    )
    assert (
        result.user.athlete_id
        == athlete.athlete_id
    )
    assert (
        result.access_grant.permission
        == "owner"
    )
    assert (
        result.invitation.is_claimed
        is True
    )

    link = repository_set[
        "identity_repository"
    ].get(
        "https://accounts.google.com",
        "google-subject-123",
    )

    assert (
        link.user_id
        == result.user.user_id
    )

    stored_invitation = repository_set[
        "invitation_repository"
    ].get(
        invitation.invitation_id
    )

    assert (
        stored_invitation
        .claimed_by_user_id
        == result.user.user_id
    )


def test_repeated_identity_resolves_same_user(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    prepare_invitation(
        repository_set
    )

    service = ProvisionInvitedUser(
        **repository_set
    )

    first = service.execute(
        external_identity()
    )

    second = service.execute(
        external_identity(
            email=(
                "changed@example.com"
            )
        )
    )

    assert second.created is False

    assert (
        second.user.user_id
        == first.user.user_id
    )

    assert len(
        repository_set[
            "user_repository"
        ].list()
    ) == 1


def test_same_verified_email_can_link_google_and_email_code(
    tmp_path,
):
    repository_set = repositories(tmp_path)
    prepare_email_only_invitation(repository_set)
    service = ProvisionInvitedUser(**repository_set)

    google_result = service.execute(
        external_identity()
    )
    email_result = service.execute(
        ExternalIdentity(
            issuer="https://example.eu.auth0.com/",
            subject="auth0-passwordless-subject",
            email="pedro@example.com",
            email_verified=True,
            name="Pedro",
        )
    )

    assert email_result.created is False
    assert email_result.user.user_id == google_result.user.user_id
    assert email_result.access_grant == google_result.access_grant
    assert len(repository_set["identity_repository"].list()) == 2


def test_unverified_identity_is_rejected(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    prepare_invitation(
        repository_set
    )

    with pytest.raises(
        PermissionError,
        match="verified",
    ):
        ProvisionInvitedUser(
            **repository_set
        ).execute(
            external_identity(
                verified=False
            )
        )

    assert (
        repository_set[
            "user_repository"
        ].list()
        == []
    )

    assert (
        repository_set[
            "identity_repository"
        ].list()
        == []
    )


def test_uninvited_email_is_rejected(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    with pytest.raises(
        PermissionError,
        match="not invited",
    ):
        ProvisionInvitedUser(
            **repository_set
        ).execute(
            external_identity()
        )

    assert (
        repository_set[
            "user_repository"
        ].list()
        == []
    )


def test_missing_invited_athlete_is_rejected(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    repository_set[
        "invitation_repository"
    ].save(
        AlphaInvitation(
            email=(
                "pedro@example.com"
            ),
            role="athlete",
            athlete_id=(
                "missing-athlete"
            ),
        )
    )

    with pytest.raises(
        RuntimeError,
        match="does not exist",
    ):
        ProvisionInvitedUser(
            **repository_set
        ).execute(
            external_identity()
        )

    assert (
        repository_set[
            "user_repository"
        ].list()
        == []
    )


def test_claimed_invitation_without_link_is_rejected(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    athlete, invitation = (
        prepare_invitation(
            repository_set
        )
    )

    repository_set[
        "invitation_repository"
    ].save(
        invitation.claim(
            "orphan-user"
        )
    )

    with pytest.raises(
        RuntimeError,
        match="already claimed",
    ):
        ProvisionInvitedUser(
            **repository_set
        ).execute(
            external_identity()
        )

    assert (
        repository_set[
            "user_repository"
        ].list()
        == []
    )



def test_provisioning_uses_transaction_context(
    tmp_path,
):

    repository_set = repositories(
        tmp_path
    )

    prepare_invitation(
        repository_set
    )

    calls = []

    class TransactionContext:

        def __enter__(
            self,
        ):

            calls.append(
                "enter"
            )

        def __exit__(
            self,
            error_type,
            error,
            traceback,
        ):

            calls.append(
                "exit"
            )

            return False

    def transaction_factory():

        return TransactionContext()

    result = ProvisionInvitedUser(
        **repository_set,
        transaction_factory=(
            transaction_factory
        ),
    ).execute(
        external_identity()
    )

    assert result.created is True

    assert calls == [
        "enter",
        "exit",
    ]
