"""
Tests for activity upload concurrency protection.
"""

from threading import (
    Event,
    Thread,
)

import pytest

from performancelab.upload_guard import (
    ActivityUploadGuard,
    ActivityUploadInProgressError,
    ActivityUploadTooSoonError,
)


def test_blocks_concurrent_import_for_same_athlete():

    guard = ActivityUploadGuard(
        cooldown_seconds=0
    )

    entered = Event()
    release = Event()
    completed = Event()

    def hold_import():

        with guard.protect(
            "athlete-1"
        ):

            entered.set()
            release.wait(
                timeout=2
            )

        completed.set()

    worker = Thread(
        target=hold_import
    )

    worker.start()

    assert entered.wait(
        timeout=2
    )

    with pytest.raises(
        ActivityUploadInProgressError,
        match="already in progress",
    ):

        with guard.protect(
            "athlete-1"
        ):

            pass

    release.set()

    worker.join(
        timeout=2
    )

    assert completed.is_set()


def test_allows_concurrent_imports_for_different_athletes():

    guard = ActivityUploadGuard(
        cooldown_seconds=0
    )

    with guard.protect(
        "athlete-1"
    ):

        with guard.protect(
            "athlete-2"
        ):

            pass


def test_blocks_rapid_repeated_import():

    current_time = [
        100.0,
    ]

    guard = ActivityUploadGuard(
        cooldown_seconds=2,
        clock=lambda: (
            current_time[0]
        ),
    )

    with guard.protect(
        "athlete-1"
    ):

        pass

    with pytest.raises(
        ActivityUploadTooSoonError,
        match="too quickly",
    ):

        with guard.protect(
            "athlete-1"
        ):

            pass

    current_time[0] += 2

    with guard.protect(
        "athlete-1"
    ):

        pass


def test_failure_releases_active_import():

    current_time = [
        100.0,
    ]

    guard = ActivityUploadGuard(
        cooldown_seconds=2,
        clock=lambda: (
            current_time[0]
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="import failed",
    ):

        with guard.protect(
            "athlete-1"
        ):

            raise RuntimeError(
                "import failed"
            )

    current_time[0] += 2

    with guard.protect(
        "athlete-1"
    ):

        pass


def test_rejects_empty_athlete_id():

    guard = ActivityUploadGuard()

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):

        with guard.protect(
            "  "
        ):

            pass