"""
PerformanceLab

Training Coach text generation boundary.

The domain-facing service is independent from any external
model provider and contains no UI or persistence logic.
"""

from collections.abc import (
    Mapping,
)
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


class ActivityCoachGenerationStatus(Enum):
    """
    Result status exposed to callers.
    """

    GENERATED = "generated"
    UNAVAILABLE = "unavailable"
    FAILED = "failed"


@dataclass(frozen=True)
class ActivityCoachNarrative:
    """
    Immutable structured narrative returned by a provider.
    """

    measured_facts: str
    deterministic_signals: str
    prudent_interpretation: str
    recommendations: str
    data_limitations: str

    provider: str
    model: str


@dataclass(frozen=True)
class ActivityCoachGenerationResult:
    """
    Immutable result of one generation attempt.
    """

    status: ActivityCoachGenerationStatus
    narrative: ActivityCoachNarrative | None = None
    error_code: str | None = None


class ActivityCoachProviderUnavailable(
    RuntimeError
):
    """
    Raised when a configured provider cannot be used.
    """


class ActivityCoachTextProvider(
    Protocol
):
    """
    Provider-neutral text generation contract.
    """

    @property
    def provider_name(
        self,
    ) -> str:
        ...

    @property
    def model_name(
        self,
    ) -> str:
        ...

    def generate(
        self,
        payload: Mapping[
            str,
            object,
        ],
    ) -> ActivityCoachNarrative:
        ...


class ActivityCoachGenerationService:
    """
    Coordinates generation through a configured provider.

    Provider exceptions are converted into stable result
    states instead of leaking into the UI.
    """

    def __init__(
        self,
        provider: (
            ActivityCoachTextProvider
            | None
        ),
    ) -> None:

        self.provider = provider

    def generate(
        self,
        payload: Mapping[
            str,
            object,
        ],
    ) -> ActivityCoachGenerationResult:

        if self.provider is None:
            return ActivityCoachGenerationResult(
                status=(
                    ActivityCoachGenerationStatus
                    .UNAVAILABLE
                ),
                error_code=(
                    "provider_not_configured"
                ),
            )

        try:
            narrative = (
                self.provider.generate(
                    payload
                )
            )

        except ActivityCoachProviderUnavailable:
            return ActivityCoachGenerationResult(
                status=(
                    ActivityCoachGenerationStatus
                    .UNAVAILABLE
                ),
                error_code=(
                    "provider_unavailable"
                ),
            )

        except Exception:
            return ActivityCoachGenerationResult(
                status=(
                    ActivityCoachGenerationStatus
                    .FAILED
                ),
                error_code=(
                    "generation_failed"
                ),
            )

        return ActivityCoachGenerationResult(
            status=(
                ActivityCoachGenerationStatus
                .GENERATED
            ),
            narrative=narrative,
        )