from datetime import (
    datetime,
    timezone,
)

import pytest

from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)


def test_creates_generated_usage_event():

    event = TrainingCoachUsageEvent(
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            24,
            18,
            0,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .GENERATED
        ),
        usage_id="usage-1",
    )

    assert event.user_id == "user-1"

    assert (
        event.status
        is TrainingCoachUsageStatus
        .GENERATED
    )

    assert (
        event.counts_toward_limit
        is True
    )


def test_failed_event_does_not_consume_allowance():

    event = TrainingCoachUsageEvent(
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            24,
            18,
            0,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .FAILED
        ),
    )

    assert (
        event.counts_toward_limit
        is False
    )


def test_normalizes_identifiers():

    event = TrainingCoachUsageEvent(
        user_id=" user-1 ",
        occurred_at=datetime(
            2026,
            8,
            24,
            18,
            0,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .GENERATED
        ),
        usage_id=" usage-1 ",
    )

    assert event.user_id == "user-1"
    assert event.usage_id == "usage-1"


def test_rejects_empty_user_id():

    with pytest.raises(
        ValueError,
        match="user_id cannot be empty",
    ):

        TrainingCoachUsageEvent(
            user_id=" ",
            occurred_at=datetime(
                2026,
                8,
                24,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
        )


def test_rejects_timestamp_without_timezone():

    with pytest.raises(
        ValueError,
        match="must include a timezone",
    ):

        TrainingCoachUsageEvent(
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                24,
                18,
                0,
            ),
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
        )


def test_rejects_plain_text_status():

    with pytest.raises(
        TypeError,
        match=(
            "status must be a "
            "TrainingCoachUsageStatus"
        ),
    ):

        TrainingCoachUsageEvent(
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                24,
                18,
                0,
                tzinfo=timezone.utc,
            ),
            status="generated",
        )