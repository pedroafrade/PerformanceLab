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



def test_records_operational_metadata():

    event = TrainingCoachUsageEvent(
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            25,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .GENERATED
        ),
        provider=" google-gemini ",
        model=" gemini-3.5-flash ",
        latency_ms=1250,
        remaining_user_requests=4,
        remaining_global_requests=49,
    )

    assert (
        event.provider
        == "google-gemini"
    )
    assert (
        event.model
        == "gemini-3.5-flash"
    )
    assert event.error_code is None
    assert event.latency_ms == 1250

    assert (
        event.remaining_user_requests
        == 4
    )
    assert (
        event.remaining_global_requests
        == 49
    )


def test_records_safe_failure_code():

    event = TrainingCoachUsageEvent(
        user_id="user-1",
        occurred_at=datetime(
            2026,
            8,
            25,
            10,
            30,
            tzinfo=timezone.utc,
        ),
        status=(
            TrainingCoachUsageStatus
            .FAILED
        ),
        provider="google-gemini",
        model="gemini-3.5-flash",
        error_code="quota",
        latency_ms=500,
        remaining_user_requests=5,
        remaining_global_requests=50,
    )

    assert event.error_code == "quota"

    assert (
        event.counts_toward_limit
        is False
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "latency_ms",
        "remaining_user_requests",
        "remaining_global_requests",
    ),
)
def test_rejects_negative_operational_count(
    field_name,
):

    values = {
        field_name: -1,
    }

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):

        TrainingCoachUsageEvent(
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                25,
                10,
                30,
                tzinfo=timezone.utc,
            ),
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
            **values,
        )


def test_rejects_empty_optional_metadata():

    with pytest.raises(
        ValueError,
        match="model cannot be empty",
    ):

        TrainingCoachUsageEvent(
            user_id="user-1",
            occurred_at=datetime(
                2026,
                8,
                25,
                10,
                30,
                tzinfo=timezone.utc,
            ),
            status=(
                TrainingCoachUsageStatus
                .GENERATED
            ),
            model=" ",
        )