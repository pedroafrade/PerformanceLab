"""
Tests for PostgreSQL private alpha consent persistence.
"""

from datetime import (
    datetime,
    timezone,
)

import pytest

from sqlalchemy import (
    create_engine,
    insert,
)

from performancelab.alpha_participation_consent import (
    ALPHA_PARTICIPATION_CONSENT_VERSION,
    AlphaParticipationConsent,
)
from performancelab.storage.postgresql_alpha_participation_consent_repository import (
    PostgreSQLAlphaParticipationConsentRepository,
)
from performancelab.storage.postgresql_schema import (
    alpha_participation_consents,
    athletes,
    metadata,
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
            alpha_participation_consents,
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

        connection.execute(
            insert(
                users
            ),
            (
                {
                    "user_id": "user-1",
                    "email": (
                        "pedro@example.com"
                    ),
                    "role": "athlete",
                    "athlete_id": (
                        "athlete-1"
                    ),
                },
                {
                    "user_id": "user-2",
                    "email": (
                        "friend@example.com"
                    ),
                    "role": "athlete",
                    "athlete_id": (
                        "athlete-1"
                    ),
                },
            ),
        )

        yield connection

        connection.rollback()

    engine.dispose()


def timestamp(
    day,
):

    return datetime(
        2026,
        8,
        day,
        12,
        0,
        tzinfo=timezone.utc,
    )


def test_saves_and_finds_consent(
    connection,
):

    repository = (
        PostgreSQLAlphaParticipationConsentRepository(
            connection
        )
    )

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        consent
    )

    assert (
        repository.latest(
            user_id="user-1",
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )
        == consent
    )


def test_persists_withdrawal(
    connection,
):

    repository = (
        PostgreSQLAlphaParticipationConsentRepository(
            connection
        )
    )

    consent = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        consent
    )

    withdrawn = consent.withdraw(
        withdrawn_at=timestamp(
            26
        )
    )

    repository.save(
        withdrawn
    )

    stored = repository.latest(
        user_id="user-1",
        notice_version=(
            ALPHA_PARTICIPATION_CONSENT_VERSION
        ),
    )

    assert stored == withdrawn
    assert stored.is_active is False


def test_lists_only_requested_user(
    connection,
):

    repository = (
        PostgreSQLAlphaParticipationConsentRepository(
            connection
        )
    )

    first = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    second = AlphaParticipationConsent(
        user_id="user-2",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        first
    )
    repository.save(
        second
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            first,
        )
    )


def test_finds_requested_notice_version(
    connection,
):

    repository = (
        PostgreSQLAlphaParticipationConsentRepository(
            connection
        )
    )

    old = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            24
        ),
        notice_version=(
            "alpha-participation-consent-old"
        ),
    )

    current = AlphaParticipationConsent(
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        old
    )
    repository.save(
        current
    )

    assert (
        repository.latest(
            user_id="user-1",
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )
        == current
    )


def test_rejects_consent_identity_change(
    connection,
):

    repository = (
        PostgreSQLAlphaParticipationConsentRepository(
            connection
        )
    )

    consent = AlphaParticipationConsent(
        consent_id="consent-1",
        user_id="user-1",
        accepted_at=timestamp(
            25
        ),
    )

    repository.save(
        consent
    )

    changed = AlphaParticipationConsent(
        consent_id="consent-1",
        user_id="user-1",
        accepted_at=timestamp(
            26
        ),
    )

    with pytest.raises(
        ValueError,
        match="cannot be changed",
    ):

        repository.save(
            changed
        )