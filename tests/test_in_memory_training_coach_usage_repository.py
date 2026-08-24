from datetime import (
    date,
    datetime,
    timedelta,
    timezone,
)

import pytest

from performancelab.storage.in_memory_training_coach_usage_repository import (
    InMemoryTrainingCoachUsageRepository,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)


def create_event(
    *,
    usage_id,
    user_id,
    occurred_at,
    status=(
        TrainingCoachUsageStatus
        .GENERATED
    ),
):

    return TrainingCoachUsageEvent(
        usage_id=usage_id,
        user_id=user_id,
        occurred_at=occurred_at,
        status=status,
    )


def test_counts_user_and_global_usage():

    repository = (
        InMemoryTrainingCoachUsageRepository(
            events=(
                create_event(
                    usage_id="usage-1",
                    user_id="user-1",
                    occurred_at=datetime(
                        2026,
                        8,
                        24,
                        10,
                        0,
                        tzinfo=timezone.utc,
                    ),
                ),
                create_event(
                    usage_id="usage-2",
                    user_id="user-1",
                    occurred_at=datetime(
                        2026,
                        8,
                        24,
                        11,
                        0,
                        tzinfo=timezone.utc,
                    ),
                ),
                create_event(
                    usage_id="usage-3",
                    user_id="user-2",
                    occurred_at=datetime(
                        2026,
                        8,
                        24,
                        12,
                        0,
                        tzinfo=timezone.utc,
                    ),
                ),
            )
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

    assert counts.user_count == 2
    assert counts.global_count == 3


def test_does_not_count_failed_request():

    repository = (
        InMemoryTrainingCoachUsageRepository(
            events=(
                create_event(
                    usage_id="usage-1",
                    user_id="user-1",
                    occurred_at=datetime(
                        2026,
                        8,
                        24,
                        10,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    status=(
                        TrainingCoachUsageStatus
                        .FAILED
                    ),
                ),
            )
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


def test_does_not_count_another_day():

    repository = (
        InMemoryTrainingCoachUsageRepository(
            events=(
                create_event(
                    usage_id="usage-1",
                    user_id="user-1",
                    occurred_at=datetime(
                        2026,
                        8,
                        23,
                        23,
                        0,
                        tzinfo=timezone.utc,
                    ),
                ),
            )
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


def test_converts_timestamp_to_utc_day():

    portugal_summer_time = timezone(
        timedelta(
            hours=1
        )
    )

    repository = (
        InMemoryTrainingCoachUsageRepository(
            events=(
                create_event(
                    usage_id="usage-1",
                    user_id="user-1",
                    occurred_at=datetime(
                        2026,
                        8,
                        24,
                        0,
                        30,
                        tzinfo=(
                            portugal_summer_time
                        ),
                    ),
                ),
            )
        )
    )

    previous_day = (
        repository
        .counts_for_utc_day(
            user_id="user-1",
            utc_day=date(
                2026,
                8,
                23,
            ),
        )
    )

    current_day = (
        repository
        .counts_for_utc_day(
            user_id="user-1",
            utc_day=date(
                2026,
                8,
                24,
            ),
        )
    )

    assert previous_day.user_count == 1
    assert current_day.user_count == 0


def test_repeated_save_does_not_duplicate_event():

    event = create_event(
        usage_id="usage-1",
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            24,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )

    repository = (
        InMemoryTrainingCoachUsageRepository()
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


def test_rejects_changed_event_with_same_id():

    repository = (
        InMemoryTrainingCoachUsageRepository()
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                24,
                10,
                0,
                tzinfo=timezone.utc,
            ),
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
                occurred_at=datetime(
                    2026,
                    8,
                    24,
                    10,
                    0,
                    tzinfo=timezone.utc,
                ),
            )
        )