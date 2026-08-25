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
from time import (
    perf_counter,
)
from typing import (
    ClassVar,
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


def monotonic_time() -> float:
    """
    Return a monotonic value for measuring duration.
    """

    return perf_counter()


class GenerateActivityCoachInterpretation:
    """
    Check limits, generate an interpretation and record usage.

    Active requests are shared by every use-case instance in
    the current application process.
    """

    _active_requests: ClassVar[
        set[
            tuple[
                str,
                str,
            ]
        ]
    ] = set()

    _active_requests_lock: ClassVar[
        Lock
    ] = Lock()

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
        timer: Callable[
            [],
            float,
        ] = monotonic_time,

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
        if not callable(
            timer
        ):

            raise TypeError(
                "timer must be callable."
            )

        self._coordinator = coordinator
        self._usage_repository = (
            usage_repository
        )
        self._usage_limits = usage_limits
        self._clock = clock
        self._timer = timer


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

    def _configured_provider_metadata(
        self,
    ) -> tuple[
        str | None,
        str | None,
    ]:
        """
        Return the configured provider identity without
        exposing provider errors or request contents.
        """

        provider = (
            self._coordinator
            .generation_service
            .provider
        )

        if provider is None:

            return (
                None,
                None,
            )

        provider_name = getattr(
            provider,
            "provider_name",
            None,
        )

        model_name = getattr(
            provider,
            "model_name",
            None,
        )

        return (
            provider_name
            if isinstance(
                provider_name,
                str,
            )
            else None,
            model_name
            if isinstance(
                model_name,
                str,
            )
            else None,
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

        started_at = self._timer()

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

            finished_at = self._timer()

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

        (
            provider_name,
            model_name,
        ) = (
            self
            ._configured_provider_metadata()
        )

        if (
            resolution.interpretation
            is not None
        ):

            provider_name = (
                resolution
                .interpretation
                .narrative
                .provider
            )

            model_name = (
                resolution
                .interpretation
                .narrative
                .model
            )

        elapsed_seconds = max(
            float(
                finished_at
            )
            - float(
                started_at
            ),
            0.0,
        )

        latency_ms = int(
            round(
                elapsed_seconds
                * 1000
            )
        )

        generated_count = (
            1
            if (
                usage_status
                is TrainingCoachUsageStatus
                .GENERATED
            )
            else 0
        )

        remaining_user_requests = max(
            (
                decision
                .remaining_user_requests
                - generated_count
            ),
            0,
        )

        remaining_global_requests = max(
            (
                decision
                .remaining_global_requests
                - generated_count
            ),
            0,
        )

        self._usage_repository.save(
            TrainingCoachUsageEvent(
                user_id=(
                    normalized_user_id
                ),
                occurred_at=occurred_at,
                status=usage_status,
                provider=provider_name,
                model=model_name,
                error_code=(
                    resolution.error_code
                ),
                latency_ms=latency_ms,
                remaining_user_requests=(
                    remaining_user_requests
                ),
                remaining_global_requests=(
                    remaining_global_requests
                ),
            )
        )

        return resolution