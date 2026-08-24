"""
Tests for immutable activity upload results.
"""

from dataclasses import (
    FrozenInstanceError,
)

import pytest

from performancelab.upload_results import (
    ActivityFileImportResult,
    ActivityUploadBatchResult,
)


def result(
    status,
    *,
    workout_id=None,
):

    return ActivityFileImportResult(
        file_name=(
            f"{status}.fit"
        ),
        status=status,
        workout_id=workout_id,
    )


def test_counts_every_file_status():

    batch = ActivityUploadBatchResult(
        files=(
            result(
                "imported",
                workout_id="workout-1",
            ),
            result(
                "updated",
                workout_id="workout-2",
            ),
            result(
                "duplicate",
                workout_id="workout-3",
            ),
            result(
                "ignored",
            ),
            result(
                "invalid",
            ),
        )
    )

    assert batch.imported_count == 1
    assert batch.updated_count == 1
    assert batch.duplicate_count == 1
    assert batch.ignored_count == 1
    assert batch.invalid_count == 1

    assert batch.notice == (
        "Import complete: "
        "1 imported, "
        "1 updated, "
        "1 duplicate, "
        "1 ignored, "
        "1 invalid."
    )


def test_processed_activity_requires_workout_id():

    with pytest.raises(
        ValueError,
        match="must have a workout_id",
    ):

        ActivityFileImportResult(
            file_name="activity.fit",
            status="imported",
        )


def test_invalid_file_can_have_safe_reason():

    file_result = (
        ActivityFileImportResult(
            file_name="broken.fit",
            status="invalid",
            reason=(
                "The activity file could "
                "not be imported."
            ),
        )
    )

    assert (
        file_result.workout_id
        is None
    )

    assert (
        file_result.reason
        == (
            "The activity file could "
            "not be imported."
        )
    )


def test_results_are_immutable():

    file_result = (
        ActivityFileImportResult(
            file_name="activity.fit",
            status="ignored",
        )
    )

    batch = ActivityUploadBatchResult(
        files=(
            file_result,
        )
    )

    with pytest.raises(
        FrozenInstanceError
    ):

        file_result.status = "invalid"

    with pytest.raises(
        FrozenInstanceError
    ):

        batch.files = ()