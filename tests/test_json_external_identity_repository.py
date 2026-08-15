import pytest

from performancelab.identity import (
    ExternalIdentity,
    ExternalIdentityLink,
)
from performancelab.storage.json_external_identity_repository import (
    JsonExternalIdentityRepository,
)


def identity():

    return ExternalIdentity(
        issuer=(
            "https://accounts.google.com"
        ),
        subject=(
            "google-subject-123"
        ),
        email=(
            "pedro@example.com"
        ),
        email_verified=True,
        name="Pedro",
    )


def test_builds_link_from_external_identity():

    link = (
        ExternalIdentityLink
        .from_identity(
            identity(),
            user_id="user-123",
        )
    )

    assert link.provider_key == (
        "https://accounts.google.com",
        "google-subject-123",
    )

    assert link.user_id == (
        "user-123"
    )


def test_save_and_get_link(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    link = (
        ExternalIdentityLink
        .from_identity(
            identity(),
            user_id="user-123",
        )
    )

    repository.save(
        link
    )

    loaded = repository.get(
        link.issuer,
        link.subject,
    )

    assert loaded == link


def test_repeated_save_is_idempotent(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    link = ExternalIdentityLink(
        issuer=(
            "https://accounts.google.com"
        ),
        subject=(
            "google-subject-123"
        ),
        user_id="user-123",
    )

    repository.save(
        link
    )
    repository.save(
        link
    )

    assert repository.list() == [
        link
    ]


def test_cannot_reassign_identity(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    first_link = ExternalIdentityLink(
        issuer=(
            "https://accounts.google.com"
        ),
        subject=(
            "google-subject-123"
        ),
        user_id="user-123",
    )

    conflicting_link = (
        ExternalIdentityLink(
            issuer=(
                "https://accounts.google.com"
            ),
            subject=(
                "google-subject-123"
            ),
            user_id="user-456",
        )
    )

    repository.save(
        first_link
    )

    with pytest.raises(
        ValueError,
        match="already linked",
    ):
        repository.save(
            conflicting_link
        )

    assert repository.get(
        first_link.issuer,
        first_link.subject,
    ) == first_link


def test_same_subject_from_different_issuer_is_distinct(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    google_link = ExternalIdentityLink(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="shared-subject",
        user_id="user-google",
    )

    another_link = ExternalIdentityLink(
        issuer=(
            "https://identity.example.com"
        ),
        subject="shared-subject",
        user_id="user-example",
    )

    repository.save(
        google_link
    )
    repository.save(
        another_link
    )

    assert len(
        repository.list()
    ) == 2


def test_delete_removes_link(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    link = ExternalIdentityLink(
        issuer=(
            "https://accounts.google.com"
        ),
        subject=(
            "google-subject-123"
        ),
        user_id="user-123",
    )

    repository.save(
        link
    )

    repository.delete(
        link.issuer,
        link.subject,
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get(
            link.issuer,
            link.subject,
        )


def test_unknown_identity_raises(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    with pytest.raises(
        KeyError,
        match="does not exist",
    ):
        repository.get(
            "https://accounts.google.com",
            "unknown-subject",
        )


def test_link_is_stored_without_email(
    tmp_path,
):

    repository = (
        JsonExternalIdentityRepository(
            tmp_path
        )
    )

    link = (
        ExternalIdentityLink
        .from_identity(
            identity(),
            user_id="user-123",
        )
    )

    repository.save(
        link
    )

    stored_text = next(
        tmp_path.glob(
            "*.json"
        )
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "pedro@example.com"
        not in stored_text
    )
    assert "Pedro" not in stored_text