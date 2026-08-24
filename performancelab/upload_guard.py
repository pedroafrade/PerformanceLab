"""
PerformanceLab

Process-level coordination for activity uploads.
"""

from contextlib import (
    contextmanager,
)
from threading import (
    Lock,
)
from time import (
    monotonic,
)


class ActivityUploadInProgressError(
    RuntimeError
):
    """
    Raised when the athlete already has an active import.
    """


class ActivityUploadTooSoonError(
    RuntimeError
):
    """
    Raised when imports are repeated too quickly.
    """


class ActivityUploadGuard:
    """
    Coordinate imports independently for each athlete.

    The guard prevents concurrent processing in one application
    process. PostgreSQL optimistic concurrency remains the
    protection between separate application processes.
    """

    def __init__(
        self,
        *,
        cooldown_seconds: float = 2.0,
        clock=monotonic,
    ) -> None:

        if cooldown_seconds < 0:

            raise ValueError(
                "cooldown_seconds cannot be negative."
            )

        self._cooldown_seconds = float(
            cooldown_seconds
        )
        self._clock = clock
        self._state_lock = Lock()
        self._active_athletes: set[str] = set()
        self._last_finished_at: dict[
            str,
            float,
        ] = {}

    @contextmanager
    def protect(
        self,
        athlete_id: str,
    ):
        """
        Protect one complete upload attempt for an athlete.
        """

        normalized_athlete_id = str(
            athlete_id
        ).strip()

        if not normalized_athlete_id:

            raise ValueError(
                "athlete_id cannot be empty."
            )

        with self._state_lock:

            if (
                normalized_athlete_id
                in self._active_athletes
            ):

                raise ActivityUploadInProgressError(
                    "An activity import is already "
                    "in progress for this athlete."
                )

            now = self._clock()

            last_finished_at = (
                self._last_finished_at.get(
                    normalized_athlete_id
                )
            )

            if (
                last_finished_at is not None
                and (
                    now
                    - last_finished_at
                )
                < self._cooldown_seconds
            ):

                raise ActivityUploadTooSoonError(
                    "Activity imports are being "
                    "repeated too quickly."
                )

            self._active_athletes.add(
                normalized_athlete_id
            )

        try:

            yield

        finally:

            finished_at = self._clock()

            with self._state_lock:

                self._active_athletes.discard(
                    normalized_athlete_id
                )

                self._last_finished_at[
                    normalized_athlete_id
                ] = finished_at


DEFAULT_ACTIVITY_UPLOAD_GUARD = (
    ActivityUploadGuard()
)