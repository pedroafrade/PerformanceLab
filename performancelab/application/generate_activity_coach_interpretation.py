"""
PerformanceLab

Limited Training Coach generation use case.
"""

from collections.abc import (
    Callable,
    Mapping,
)
from datetime import (
    datetime,
    timezone,
)
from threading import (
    Lock,
)
from performancelab.coaching import (
    ActivityCoachCoordinator,
    ActivityCoachResolutionResult,
    ActivityCoachResolutionStatus,
)
from performancelab.storage.training_coach_usage_repository import (
    TrainingCoachUsageRepository,
)
from performancelab.training_coach_usage import (
    TrainingCoachUsageEvent,
    TrainingCoachUsageStatus,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageLimits,
)


def current_utc_time() -> datetime:
    """
    Return the current timezone-aware UTC time.
    """

    return datetime.now(
        timezone.utc
    )


class GenerateActivityCoachInterpretation:
    """
    Check limits, generate an interpretation and record usage.
    """

    def __init__(
        self,
        *,
        coordinator: ActivityCoachCoordinator,
        usage_repository: (
            TrainingCoachUsageRepository
        ),
        usage_limits: (
            TrainingCoachUsageLimits
        ),
        clock: Callable[
            [],
            datetime,
        ] = current_utc_time,
    ) -> None:

        if not isinstance(
            coordinator,
            ActivityCoachCoordinator,
        ):

            raise TypeError(
                "coordinator must be an "
                "ActivityCoachCoordinator."
            )

        if not isinstance(
            usage_limits,
            TrainingCoachUsageLimits,
        ):

            raise TypeError(
                "usage_limits must be "
                "TrainingCoachUsageLimits."
            )

        if not callable(
            clock
        ):

            raise TypeError(
                "clock must be callable."
            )

        self._coordinator = coordinator
        self._usage_repository = (
            usage_repository
        )
        self._usage_limits = usage_limits
        self._clock = clock

        self._active_requests: set[
            tuple[
                str,
                str,
            ]
        ] = set()

        self._active_requests_lock = (
            Lock()
        )

    @staticmethod
    def _normalized_user_id(
        user_id,
    ) -> str:

        if not isinstance(
            user_id,
            str,
        ):

            raise TypeError(
                "user_id must be a string."
            )

        normalized_user_id = (
            user_id.strip()
        )

        if not normalized_user_id:

            raise ValueError(
                "user_id cannot be empty."
            )

        return normalized_user_id

    @staticmethod
    def _validated_time(
        value,
    ) -> datetime:

        if not isinstance(
            value,
            datetime,
        ):

            raise TypeError(
                "clock must return a datetime."
            )

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):

            raise ValueError(
                "clock must return a "
                "timezone-aware datetime."
            )

        return value.astimezone(
            timezone.utc
        )

    def execute(
        self,
        *,
        user_id: str,
        athlete,
        workout_id: str,
        payload: Mapping[
            str,
            object,
        ],
        regenerate: bool = False,
    ) -> ActivityCoachResolutionResult:

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        occurred_at = (
            self._validated_time(
                self._clock()
            )
        )

        counts = (
            self._usage_repository
            .counts_for_utc_day(
                user_id=(
                    normalized_user_id
                ),
                utc_day=(
                    occurred_at.date()
                ),
            )
        )

        decision = (
            self._usage_limits
            .evaluate(
                counts
            )
        )

        if not decision.permitted:

            return ActivityCoachResolutionResult(
                status=(
                    ActivityCoachResolutionStatus
                    .LIMIT_REACHED
                ),
                error_code=decision.reason,
            )

        request_key = (
            normalized_user_id,
            str(
                workout_id
            ).strip(),
        )

        with self._active_requests_lock:

            if (
                request_key
                in self._active_requests
            ):

                return (
                    ActivityCoachResolutionResult(
                        status=(
                            ActivityCoachResolutionStatus
                            .IN_PROGRESS
                        ),
                        error_code=(
                            "generation_in_progress"
                        ),
                    )
                )

            self._active_requests.add(
                request_key
            )

        try:

            resolution = (
                self._coordinator
                .resolve(
                    athlete=athlete,
                    workout_id=workout_id,
                    payload=payload,
                    regenerate=regenerate,
                )
            )

        finally:

            with (
                self._active_requests_lock
            ):

                self._active_requests.discard(
                    request_key
                )

        usage_status = (
            TrainingCoachUsageStatus
            .GENERATED
            if (
                resolution.status
                is ActivityCoachResolutionStatus
                .GENERATED
            )
            else (
                TrainingCoachUsageStatus
                .FAILED
            )
        )

        self._usage_repository.save(
            TrainingCoachUsageEvent(
                user_id=(
                    normalized_user_id
                ),
                occurred_at=occurred_at,
                status=usage_status,
            )
        )

        return resolution