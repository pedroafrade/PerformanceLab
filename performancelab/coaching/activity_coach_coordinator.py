"""
PerformanceLab

Training Coach generation and reuse coordinator.
"""

from collections.abc import (
    Callable,
    Mapping,
)
from dataclasses import dataclass
from datetime import (
    datetime,
    timezone,
)
from enum import Enum

from performancelab.activity_coach_records import (
    ActivityCoachInterpretation,
    activity_coach_context_hash,
)

from .activity_coach_generation import (
    ActivityCoachGenerationService,
    ActivityCoachGenerationStatus,
)


class ActivityCoachResolutionStatus(Enum):
    """
    Final interpretation resolution state.
    """

    STORED = "stored"
    GENERATED = "generated"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"
    LIMIT_REACHED = "limit_reached"
    IN_PROGRESS = "in_progress"


@dataclass(frozen=True)
class ActivityCoachResolutionResult:
    """
    Immutable result returned to presentation or UI code.
    """

    status: ActivityCoachResolutionStatus
    interpretation: (
        ActivityCoachInterpretation
        | None
    ) = None
    error_code: str | None = None


def _utc_now() -> datetime:

    return datetime.now(
        timezone.utc
    )


class ActivityCoachCoordinator:
    """
    Reuses or generates one activity interpretation.

    Persistence to disk remains the caller's responsibility.
    This coordinator updates the athlete's persistent domain
    collection only after successful generation.
    """

    def __init__(
        self,
        *,
        generation_service: (
            ActivityCoachGenerationService
        ),
        now: Callable[
            [],
            datetime,
        ] = _utc_now,
    ) -> None:

        self.generation_service = (
            generation_service
        )
        self.now = now

    def resolve(
        self,
        *,
        athlete,
        workout_id: str,
        payload: Mapping[
            str,
            object,
        ],
        regenerate: bool = False,
    ) -> ActivityCoachResolutionResult:

        contract_version = payload.get(
            "contract_version"
        )

        if not isinstance(
            contract_version,
            str,
        ) or not contract_version:
            return ActivityCoachResolutionResult(
                status=(
                    ActivityCoachResolutionStatus
                    .FAILED
                ),
                error_code=(
                    "invalid_contract_version"
                ),
            )

        context_hash = (
            activity_coach_context_hash(
                payload
            )
        )

        stored = (
            athlete
            .activity_coach_interpretations
            .find(
                workout_id=workout_id,
                contract_version=(
                    contract_version
                ),
                context_hash=(
                    context_hash
                ),
            )
        )

        if (
            stored is not None
            and not regenerate
        ):
            return ActivityCoachResolutionResult(
                status=(
                    ActivityCoachResolutionStatus
                    .STORED
                ),
                interpretation=stored,
            )

        generation = (
            self.generation_service
            .generate(
                payload
            )
        )

        if (
            generation.status
            is ActivityCoachGenerationStatus
            .UNAVAILABLE
        ):
            return ActivityCoachResolutionResult(
                status=(
                    ActivityCoachResolutionStatus
                    .UNAVAILABLE
                ),
                error_code=(
                    generation.error_code
                ),
            )

        if (
            generation.status
            is ActivityCoachGenerationStatus
            .FAILED
            or generation.narrative is None
        ):
            return ActivityCoachResolutionResult(
                status=(
                    ActivityCoachResolutionStatus
                    .FAILED
                ),
                error_code=(
                    generation.error_code
                    or "generation_failed"
                ),
            )

        interpretation = (
            ActivityCoachInterpretation(
                workout_id=workout_id,
                contract_version=(
                    contract_version
                ),
                context_hash=context_hash,
                generated_at=self.now(),
                narrative=(
                    generation.narrative
                ),
            )
        )

        athlete.activity_coach_interpretations.add(
            interpretation
        )

        return ActivityCoachResolutionResult(
            status=(
                ActivityCoachResolutionStatus
                .GENERATED
            ),
            interpretation=(
                interpretation
            ),
        )