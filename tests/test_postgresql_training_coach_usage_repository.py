"""
Tests for PostgreSQL Training Coach usage persistence.
"""

from datetime import (
    date,
    datetime,
    timezone,
)

import pytest

from sqlalchemy import (
    create_engine,
    insert,
    select,
)

from performancelab.storage.postgresql_schema import (
    athletes,
    metadata,
    training_coach_usage,
    users,
)
from performancelab.storage.postgresql_training_coach_usage_repository import (
    PostgreSQLTrainingCoachUsageRepository,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
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
            training_coach_usage,
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


def create_event(
    *,
    usage_id,
    user_id,
    hour,
    status=(
        TrainingCoachUsageStatus
        .GENERATED
    ),
):

    return TrainingCoachUsageEvent(
        usage_id=usage_id,
        user_id=user_id,
        occurred_at=datetime(
            2026,
            8,
            24,
            hour,
            0,
            tzinfo=timezone.utc,
        ),
        status=status,
    )


def test_saves_and_counts_usage(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
            hour=10,
        )
    )

    repository.save(
        create_event(
            usage_id="usage-2",
            user_id="user-2",
            hour=11,
        )
    )

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=date(
            2026,
            8,
            24,
        ),
    )

    assert counts.user_count == 1
    assert counts.global_count == 2


def test_does_not_count_failed_usage(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
            hour=10,
            status=(
                TrainingCoachUsageStatus
                .FAILED
            ),
        )
    )

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=date(
            2026,
            8,
            24,
        ),
    )

    assert counts.user_count == 0
    assert counts.global_count == 0


def test_repeated_save_is_idempotent(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    event = create_event(
        usage_id="usage-1",
        user_id="user-1",
        hour=10,
    )

    repository.save(
        event
    )

    repository.save(
        event
    )

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=date(
            2026,
            8,
            24,
        ),
    )

    assert counts.user_count == 1
    assert counts.global_count == 1


def test_rejects_changed_event_with_same_id(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
            hour=10,
        )
    )

    with pytest.raises(
        ValueError,
        match="usage_id already belongs",
    ):

        repository.save(
            create_event(
                usage_id="usage-1",
                user_id="user-2",
                hour=10,
            )
        )


def test_does_not_count_previous_day(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    repository.save(
        TrainingCoachUsageEvent(
            usage_id="usage-1",
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                23,
                23,
                59,
                tzinfo=timezone.utc,
            ),
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
        )
    )

    counts = repository.counts_for_utc_day(
        user_id="user-1",
        utc_day=date(
            2026,
            8,
            24,
        ),
    )

    assert counts.user_count == 0
    assert counts.global_count == 0



def test_saves_operational_metadata(
    connection,
):

    repository = (
        PostgreSQLTrainingCoachUsageRepository(
            connection
        )
    )

    event = TrainingCoachUsageEvent(
        usage_id="usage-metadata",
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            24,
            12,
            0,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .FAILED
        ),
        provider="google-gemini",
        model="gemini-3.5-flash",
        error_code="quota",
        latency_ms=750,
        remaining_user_requests=3,
        remaining_global_requests=42,
    )

    repository.save(
        event
    )

    row = connection.execute(
        select(
            training_coach_usage
        ).where(
            training_coach_usage
            .c
            .usage_id
            == "usage-metadata"
        )
    ).mappings().one()

    assert (
        row["provider"]
        == "google-gemini"
    )
    assert (
        row["model"]
        == "gemini-3.5-flash"
    )
    assert row["error_code"] == "quota"
    assert row["latency_ms"] == 750

    assert (
        row["remaining_user_requests"]
        == 3
    )
    assert (
        row["remaining_global_requests"]
        == 42
    )

    repository.save(
        event
    )