"""
PerformanceLab

Privacy-safe operational logging for activity uploads.
"""

from dataclasses import (
    dataclass,
)
import logging

from performancelab.upload_results import (
    ActivityUploadBatchResult,
)


_LOGGER = logging.getLogger(
    "performancelab.activity_upload"
)


@dataclass(
    frozen=True
)
class ActivityUploadLogSummary:
    """
    Privacy-safe upload counts suitable for operational logs.

    File names, paths, workout identifiers, raw content and
    physiological data are deliberately excluded.
    """

    total_count: int
    imported_count: int
    updated_count: int
    duplicate_count: int
    ignored_count: int
    invalid_count: int


def build_activity_upload_log_summary(
    batch_result: ActivityUploadBatchResult,
) -> ActivityUploadLogSummary:
    """
    Build a safe operational summary from an upload result.
    """

    if not isinstance(
        batch_result,
        ActivityUploadBatchResult,
    ):

        raise TypeError(
            "batch_result must be an "
            "ActivityUploadBatchResult."
        )

    return ActivityUploadLogSummary(
        total_count=len(
            batch_result.files
        ),
        imported_count=(
            batch_result.imported_count
        ),
        updated_count=(
            batch_result.updated_count
        ),
        duplicate_count=(
            batch_result.duplicate_count
        ),
        ignored_count=(
            batch_result.ignored_count
        ),
        invalid_count=(
            batch_result.invalid_count
        ),
    )


def log_activity_upload_completed(
    batch_result: ActivityUploadBatchResult,
    *,
    logger=None,
) -> None:
    """
    Log only privacy-safe counts for a completed upload batch.
    """

    summary = (
        build_activity_upload_log_summary(
            batch_result
        )
    )

    active_logger = (
        logger
        if logger is not None
        else _LOGGER
    )

    active_logger.info(
        (
            "activity_upload_completed "
            "total=%d "
            "imported=%d "
            "updated=%d "
            "duplicate=%d "
            "ignored=%d "
            "invalid=%d"
        ),
        summary.total_count,
        summary.imported_count,
        summary.updated_count,
        summary.duplicate_count,
        summary.ignored_count,
        summary.invalid_count,
    )


def log_activity_upload_failed(
    *,
    logger=None,
) -> None:
    """
    Log a generic upload failure without exception contents.
    """

    active_logger = (
        logger
        if logger is not None
        else _LOGGER
    )

    active_logger.warning(
        "activity_upload_failed"
    )