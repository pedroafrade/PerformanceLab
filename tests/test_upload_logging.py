"""
Tests for privacy-safe activity upload logging.
"""

import logging

from performancelab.upload_logging import (
    ActivityUploadLogSummary,
    build_activity_upload_log_summary,
    log_activity_upload_completed,
    log_activity_upload_failed,
)
from performancelab.upload_results import (
    ActivityFileImportResult,
    ActivityUploadBatchResult,
)


def private_batch_result():
    """
    Return results containing data that must never reach logs.
    """

    return ActivityUploadBatchResult(
        files=(
            ActivityFileImportResult(
                file_name=(
                    r"C:\Users\Pedro\Health"
                    r"\private-activity.fit"
                ),
                status="imported",
                workout_id=(
                    "private-workout-id"
                ),
                reason=(
                    "Heart rate 186 bpm and "
                    "VO2max 52.4 ml/kg/min"
                ),
            ),
            ActivityFileImportResult(
                file_name=(
                    "/home/pedro/private/"
                    "broken-activity.gpx"
                ),
                status="invalid",
                reason=(
                    "Raw physiological payload"
                ),
            ),
        )
    )


def test_builds_safe_upload_log_summary():

    summary = (
        build_activity_upload_log_summary(
            private_batch_result()
        )
    )

    assert isinstance(
        summary,
        ActivityUploadLogSummary,
    )

    assert summary.total_count == 2
    assert summary.imported_count == 1
    assert summary.updated_count == 0
    assert summary.duplicate_count == 0
    assert summary.ignored_count == 0
    assert summary.invalid_count == 1

    assert not hasattr(
        summary,
        "file_name",
    )

    assert not hasattr(
        summary,
        "workout_id",
    )

    assert not hasattr(
        summary,
        "reason",
    )


def test_completed_upload_log_excludes_private_data(
    caplog,
):

    caplog.set_level(
        logging.INFO,
        logger=(
            "performancelab.activity_upload"
        ),
    )

    log_activity_upload_completed(
        private_batch_result()
    )

    message = caplog.text

    assert (
        "activity_upload_completed"
        in message
    )
    assert "total=2" in message
    assert "imported=1" in message
    assert "invalid=1" in message

    assert "Pedro" not in message
    assert "private-activity.fit" not in message
    assert "broken-activity.gpx" not in message
    assert "private-workout-id" not in message
    assert "186 bpm" not in message
    assert "VO2max" not in message
    assert "physiological" not in message
    assert "C:\\" not in message
    assert "/home/" not in message


def test_failed_upload_log_is_generic(
    caplog,
):

    caplog.set_level(
        logging.WARNING,
        logger=(
            "performancelab.activity_upload"
        ),
    )

    log_activity_upload_failed()

    assert (
        "activity_upload_failed"
        in caplog.text
    )

    assert "Exception" not in caplog.text
    assert "Traceback" not in caplog.text