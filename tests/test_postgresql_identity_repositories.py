"""
Tests for the PostgreSQL identity repositories.
"""

import pytest

from sqlalchemy import (
    create_engine,
    insert,
)

from performancelab.identity import (
    ExternalIdentityLink,
    User,
)
from performancelab.storage.postgresql_external_identity_repository import (
    PostgreSQLExternalIdentityRepository,
)
from performancelab.storage.postgresql_schema import (
    athletes,
    external_identities,
    metadata,
    users,
)
from performancelab.storage.postgresql_user_repository import (
    PostgreSQLUserRepository,
)


@pytest.fixture
def connection():

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    metadata.create_all(
        engine,
        tables=(
            athletes,
            users,
            external_identities,
        ),
    )

    with engine.connect() as connection:

        connection.execute(
            insert(
                athletes
            ).values(
                athlete_id="athlete-1",
                name="Pedro",
            )
        )

        yield connection

        connection.rollback()

    engine.dispose()


@pytest.fixture
def user_repository(
    connection,
):

    return PostgreSQLUserRepository(
        connection
    )


@pytest.fixture
def identity_repository(
    connection,
):

    return (
        PostgreSQLExternalIdentityRepository(
            connection
        )
    )


def athlete_user(
    *,
    user_id="user-1",
    email="pedro@example.com",
):

    return User(
        user_id=user_id,
        email=email,
        role="athlete",
        athlete_id="athlete-1",
    )


def test_user_repository_saves_and_gets_user(
    user_repository,
):

    user = athlete_user()

    user_repository.save(
        user
    )

    assert (
        user_repository.get(
            "user-1"
        )
        == user
    )

    assert (
        user_repository.get_by_email(
            " PEDRO@EXAMPLE.COM "
        )
        == user
    )


def test_user_repository_updates_existing_user(
    user_repository,
):

    user_repository.save(
        athlete_user()
    )

    updated = athlete_user(
        email="updated@example.com"
    )

    user_repository.save(
        updated
    )

    assert (
        user_repository.get(
            "user-1"
        ).email
        == "updated@example.com"
    )


def test_user_repository_lists_users_by_email(
    user_repository,
):

    second_user = User(
        user_id="user-2",
        email="ana@example.com",
        role="coach",
    )

    user_repository.save(
        athlete_user()
    )
    user_repository.save(
        second_user
    )

    assert [
        user.email
        for user
        in user_repository.list()
    ] == [
        "ana@example.com",
        "pedro@example.com",
    ]


def test_user_repository_deletes_user(
    user_repository,
):

    user_repository.save(
        athlete_user()
    )

    user_repository.delete(
        "user-1"
    )

    with pytest.raises(
        KeyError
    ):
        user_repository.get(
            "user-1"
        )


def test_user_repository_reports_missing_records(
    user_repository,
):

    with pytest.raises(
        KeyError
    ):
        user_repository.get(
            "missing-user"
        )

    with pytest.raises(
        KeyError
    ):
        user_repository.get_by_email(
            "missing@example.com"
        )

    with pytest.raises(
        KeyError
    ):
        user_repository.delete(
            "missing-user"
        )


def test_external_identity_repository_saves_and_gets_link(
    user_repository,
    identity_repository,
):

    user_repository.save(
        athlete_user()
    )

    link = ExternalIdentityLink(
        issuer="https://accounts.google.com",
        subject="google-subject-1",
        user_id="user-1",
    )

    identity_repository.save(
        link
    )

    assert (
        identity_repository.get(
            " https://accounts.google.com ",
            " google-subject-1 ",
        )
        == link
    )


def test_external_identity_save_is_idempotent(
    user_repository,
    identity_repository,
):

    user_repository.save(
        athlete_user()
    )

    link = ExternalIdentityLink(
        issuer="https://accounts.google.com",
        subject="google-subject-1",
        user_id="user-1",
    )

    identity_repository.save(
        link
    )
    identity_repository.save(
        link
    )

    assert (
        identity_repository.list()
        == [
            link,
        ]
    )


def test_external_identity_cannot_be_reassigned(
    user_repository,
    identity_repository,
):

    user_repository.save(
        athlete_user()
    )

    user_repository.save(
        User(
            user_id="user-2",
            email="coach@example.com",
            role="coach",
        )
    )

    identity_repository.save(
        ExternalIdentityLink(
            issuer="https://accounts.google.com",
            subject="google-subject-1",
            user_id="user-1",
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "already linked to another user"
        ),
    ):
        identity_repository.save(
            ExternalIdentityLink(
                issuer="https://accounts.google.com",
                subject="google-subject-1",
                user_id="user-2",
            )
        )


def test_external_identity_repository_lists_and_deletes_links(
    user_repository,
    identity_repository,
):

    user_repository.save(
        athlete_user()
    )

    links = (
        ExternalIdentityLink(
            issuer="provider-b",
            subject="subject-b",
            user_id="user-1",
        ),
        ExternalIdentityLink(
            issuer="provider-a",
            subject="subject-a",
            user_id="user-1",
        ),
    )

    for link in links:
        identity_repository.save(
            link
        )

    assert (
        identity_repository.list()
        == [
            links[1],
            links[0],
        ]
    )

    identity_repository.delete(
        "provider-a",
        "subject-a",
    )

    assert (
        identity_repository.list()
        == [
            links[0],
        ]
    )


def test_external_identity_repository_reports_missing_link(
    identity_repository,
):

    with pytest.raises(
        KeyError
    ):
        identity_repository.get(
            "missing-provider",
            "missing-subject",
        )

    with pytest.raises(
        KeyError
    ):
        identity_repository.delete(
            "missing-provider",
            "missing-subject",
        )