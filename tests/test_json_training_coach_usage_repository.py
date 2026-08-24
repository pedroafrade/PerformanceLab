from datetime import (
    date,
    datetime,
    timezone,
)

import pytest

from performancelab.storage.json_training_coach_usage_repository import (
    JsonTrainingCoachUsageRepository,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)


def create_event(
    *,
    usage_id="usage-1",
    user_id="user-1",
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
            18,
            0,
            tzinfo=timezone.utc,
        ),
        status=status,
    )


def test_saves_and_loads_usage_event(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    event = create_event()

    repository.save(
        event
    )

    reloaded_repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    assert (
        reloaded_repository.list()
        == (
            event,
        )
    )


def test_counts_usage_after_repository_restart(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
        )
    )

    repository.save(
        create_event(
            usage_id="usage-2",
            user_id="user-2",
        )
    )

    reloaded_repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    counts = (
        reloaded_repository
        .counts_for_utc_day(
            user_id="user-1",
            utc_day=date(
                2026,
                8,
                24,
            ),
        )
    )

    assert counts.user_count == 1
    assert counts.global_count == 2


def test_does_not_count_failed_event(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    repository.save(
        create_event(
            status=(
                TrainingCoachUsageStatus
                .FAILED
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


def test_repeated_save_is_idempotent(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    event = create_event()

    repository.save(
        event
    )

    repository.save(
        event
    )

    assert repository.list() == (
        event,
    )


def test_rejects_changed_event_with_same_id(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    repository.save(
        create_event(
            usage_id="usage-1",
            user_id="user-1",
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
            )
        )


def test_saved_file_contains_no_activity_payload(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    repository.save(
        create_event()
    )

    saved_text = (
        (
            tmp_path
            / "usage-1.json"
        )
        .read_text(
            encoding="utf-8"
        )
    )

    assert "user-1" in saved_text
    assert "generated" in saved_text

    assert "heart_rate" not in saved_text
    assert "feedback" not in saved_text
    assert "interpretation" not in saved_text