"""
Tests for PostgreSQL invitation and access repositories.
"""

import pytest

from sqlalchemy import (
    create_engine,
    insert,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.storage.postgresql_alpha_invitation_repository import (
    PostgreSQLAlphaInvitationRepository,
)
from performancelab.storage.postgresql_athlete_access_repository import (
    PostgreSQLAthleteAccessRepository,
)
from performancelab.storage.postgresql_schema import (
    alpha_invitations,
    athletes,
    metadata,
    user_athlete_access,
    users,
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
            user_athlete_access,
            alpha_invitations,
        ),
    )

    with engine.connect() as connection:

        connection.execute(
            insert(
                athletes
            ),
            (
                {
                    "athlete_id": "athlete-1",
                    "name": "Pedro",
                },
                {
                    "athlete_id": "athlete-2",
                    "name": "Ana",
                },
            ),
        )

        connection.execute(
            insert(
                users
            ),
            (
                {
                    "user_id": "user-1",
                    "email": "pedro@example.com",
                    "role": "athlete",
                    "athlete_id": "athlete-1",
                },
                {
                    "user_id": "user-2",
                    "email": "coach@example.com",
                    "role": "coach",
                    "athlete_id": None,
                },
            ),
        )

        yield connection

        connection.rollback()

    engine.dispose()


@pytest.fixture
def invitation_repository(
    connection,
):

    return (
        PostgreSQLAlphaInvitationRepository(
            connection
        )
    )


@pytest.fixture
def access_repository(
    connection,
):

    return (
        PostgreSQLAthleteAccessRepository(
            connection
        )
    )


def invitation(
    *,
    invitation_id="invitation-1",
    email="friend@example.com",
):

    return AlphaInvitation(
        invitation_id=invitation_id,
        email=email,
        role="athlete",
        athlete_id="athlete-1",
    )


def test_invitation_repository_saves_and_gets_invitation(
    invitation_repository,
):

    expected = invitation()

    invitation_repository.save(
        expected
    )

    assert (
        invitation_repository.get(
            " invitation-1 "
        )
        == expected
    )

    assert (
        invitation_repository.get_by_email(
            " FRIEND@EXAMPLE.COM "
        )
        == expected
    )


def test_invitation_repository_updates_claimed_invitation(
    invitation_repository,
):

    original = invitation()

    invitation_repository.save(
        original
    )

    claimed = original.claim(
        "user-1"
    )

    invitation_repository.save(
        claimed
    )

    assert (
        invitation_repository.get(
            "invitation-1"
        )
        == claimed
    )


def test_invitation_repository_preserves_unique_email(
    invitation_repository,
):

    invitation_repository.save(
        invitation()
    )

    with pytest.raises(
        ValueError,
        match=(
            "invitation already exists"
        ),
    ):
        invitation_repository.save(
            invitation(
                invitation_id=(
                    "invitation-2"
                )
            )
        )


def test_invitation_repository_lists_and_deletes(
    invitation_repository,
):

    first = invitation(
        invitation_id="invitation-1",
        email="zeta@example.com",
    )
    second = invitation(
        invitation_id="invitation-2",
        email="alpha@example.com",
    )

    invitation_repository.save(
        first
    )
    invitation_repository.save(
        second
    )

    assert (
        invitation_repository.list()
        == [
            second,
            first,
        ]
    )

    invitation_repository.delete(
        "invitation-1"
    )

    assert (
        invitation_repository.list()
        == [
            second,
        ]
    )


def test_invitation_repository_reports_missing_records(
    invitation_repository,
):

    with pytest.raises(
        KeyError
    ):
        invitation_repository.get(
            "missing"
        )

    with pytest.raises(
        KeyError
    ):
        invitation_repository.get_by_email(
            "missing@example.com"
        )

    with pytest.raises(
        KeyError
    ):
        invitation_repository.delete(
            "missing"
        )


def test_access_repository_saves_and_gets_grant(
    access_repository,
):

    expected = AthleteAccessGrant(
        user_id="user-1",
        athlete_id="athlete-1",
        permission="owner",
    )

    access_repository.save(
        expected
    )

    assert (
        access_repository.get(
            " user-1 ",
            " athlete-1 ",
        )
        == expected
    )


def test_access_repository_save_is_idempotent(
    access_repository,
):

    grant = AthleteAccessGrant(
        user_id="user-1",
        athlete_id="athlete-1",
        permission="owner",
    )

    access_repository.save(
        grant
    )
    access_repository.save(
        grant
    )

    assert (
        access_repository.list()
        == [
            grant,
        ]
    )


def test_access_repository_rejects_silent_permission_change(
    access_repository,
):

    access_repository.save(
        AthleteAccessGrant(
            user_id="user-2",
            athlete_id="athlete-1",
            permission="coach",
        )
    )

    with pytest.raises(
        ValueError,
        match=(
            "cannot be changed silently"
        ),
    ):
        access_repository.save(
            AthleteAccessGrant(
                user_id="user-2",
                athlete_id="athlete-1",
                permission="owner",
            )
        )


def test_access_repository_filters_and_deletes_grants(
    access_repository,
):

    owner = AthleteAccessGrant(
        user_id="user-1",
        athlete_id="athlete-1",
        permission="owner",
    )
    coach_first = AthleteAccessGrant(
        user_id="user-2",
        athlete_id="athlete-1",
        permission="coach",
    )
    coach_second = AthleteAccessGrant(
        user_id="user-2",
        athlete_id="athlete-2",
        permission="coach",
    )

    for grant in (
        owner,
        coach_first,
        coach_second,
    ):
        access_repository.save(
            grant
        )

    assert (
        access_repository.list_for_user(
            "user-2"
        )
        == [
            coach_first,
            coach_second,
        ]
    )

    assert (
        access_repository.list_for_athlete(
            "athlete-1"
        )
        == [
            owner,
            coach_first,
        ]
    )

    access_repository.delete(
        "user-2",
        "athlete-2",
    )

    assert (
        access_repository.list()
        == [
            owner,
            coach_first,
        ]
    )


def test_access_repository_reports_missing_grant(
    access_repository,
):

    with pytest.raises(
        KeyError
    ):
        access_repository.get(
            "user-1",
            "athlete-1",
        )

    with pytest.raises(
        KeyError
    ):
        access_repository.delete(
            "user-1",
            "athlete-1",
        )