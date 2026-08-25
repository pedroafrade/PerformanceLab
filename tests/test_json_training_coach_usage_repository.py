import json

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
    provider=None,
    model=None,
    error_code=None,
    latency_ms=None,
    remaining_user_requests=None,
    remaining_global_requests=None,
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
        provider=provider,
        model=model,
        error_code=error_code,
        latency_ms=latency_ms,
        remaining_user_requests=(
            remaining_user_requests
        ),
        remaining_global_requests=(
            remaining_global_requests
        ),
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



def test_saves_operational_metadata(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    event = create_event(
        provider="google-gemini",
        model="gemini-3.5-flash",
        latency_ms=1250,
        remaining_user_requests=4,
        remaining_global_requests=49,
    )

    repository.save(
        event
    )

    loaded_event = (
        repository.list()[0]
    )

    assert loaded_event == event

    saved_data = json.loads(
        (
            tmp_path
            / "usage-1.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    assert saved_data["version"] == 2

    assert (
        saved_data["provider"]
        == "google-gemini"
    )
    assert (
        saved_data["model"]
        == "gemini-3.5-flash"
    )
    assert (
        saved_data["latency_ms"]
        == 1250
    )
    assert (
        saved_data[
            "remaining_user_requests"
        ]
        == 4
    )
    assert (
        saved_data[
            "remaining_global_requests"
        ]
        == 49
    )


def test_loads_legacy_usage_version(
    tmp_path,
):

    legacy_data = {
        "version": 1,
        "usage_id": "legacy-usage",
        "user_id": "user-1",
        "occurred_at": (
            "2026-08-24T18:00:00+00:00"
        ),
        "status": "generated",
    }

    (
        tmp_path
        / "legacy-usage.json"
    ).write_text(
        json.dumps(
            legacy_data
        ),
        encoding="utf-8",
    )

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    event = repository.list()[0]

    assert (
        event.usage_id
        == "legacy-usage"
    )
    assert event.provider is None
    assert event.model is None
    assert event.error_code is None
    assert event.latency_ms is None

    assert (
        event.remaining_user_requests
        is None
    )
    assert (
        event.remaining_global_requests
        is None
    )


def test_saved_metadata_contains_no_coach_content(
    tmp_path,
):

    repository = (
        JsonTrainingCoachUsageRepository(
            tmp_path
        )
    )

    repository.save(
        create_event(
            provider="google-gemini",
            model="gemini-3.5-flash",
            error_code="quota",
            latency_ms=400,
            remaining_user_requests=5,
            remaining_global_requests=50,
        )
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

    assert "heart_rate" not in saved_text
    assert "feedback" not in saved_text
    assert "interpretation" not in saved_text
    assert "measured_facts" not in saved_text
    assert "recommendations" not in saved_text