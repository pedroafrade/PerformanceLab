"""
Tests for PostgreSQL Training Coach consent persistence.
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

from performancelab.storage.postgresql_schema import (
    athletes,
    metadata,
    training_coach_consents,
    users,
)
from performancelab.storage.postgresql_training_coach_consent_repository import (
    PostgreSQLTrainingCoachConsentRepository,
)
from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
    TrainingCoachConsent,
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
            training_coach_consents,
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
            ).values(
                user_id="user-1",
                email="pedro@example.com",
                role="athlete",
                athlete_id="athlete-1",
            )
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
        PostgreSQLTrainingCoachConsentRepository(
            connection
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    assert (
        repository.latest(
            user_id="user-1",
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )
        == consent
    )


def test_persists_withdrawal(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachConsentRepository(
            connection
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    withdrawn = consent.withdraw(
        withdrawn_at=timestamp(
            25
        )
    )

    repository.save(
        withdrawn
    )

    stored = repository.latest(
        user_id="user-1",
        policy_version=(
            TRAINING_COACH_CONSENT_VERSION
        ),
    )

    assert stored == withdrawn
    assert stored.is_active is False


def test_lists_user_consent_history(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachConsentRepository(
            connection
        )
    )

    older = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            23
        ),
        policy_version=(
            "training-coach-consent-old"
        ),
    )

    current = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        current
    )
    repository.save(
        older
    )

    assert (
        repository.list_for_user(
            "user-1"
        )
        == (
            older,
            current,
        )
    )


def test_rejects_consent_identity_change(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachConsentRepository(
            connection
        )
    )

    consent = TrainingCoachConsent(
        user_id="user-1",
        granted_at=timestamp(
            24
        ),
    )

    repository.save(
        consent
    )

    changed = TrainingCoachConsent(
        consent_id=(
            consent.consent_id
        ),
        user_id="user-1",
        granted_at=timestamp(
            25
        ),
    )

    with pytest.raises(
        ValueError,
        match="cannot be changed",
    ):

        repository.save(
            changed
        )