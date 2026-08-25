"""
PerformanceLab

Factual Training Coach usage records.
"""

from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
)
from enum import (
    Enum,
)
from uuid import (
    uuid4,
)


class TrainingCoachUsageStatus(
    Enum
):
    """
    Final result of one Training Coach request.
    """

    GENERATED = "generated"
    FAILED = "failed"


def _validated_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require non-empty text.
    """

    if not isinstance(
        value,
        str,
    ):

        raise TypeError(
            f"{field_name} must be a string."
        )

    normalized_value = (
        value.strip()
    )

    if not normalized_value:

        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized_value


def _validated_optional_text(
    value,
    *,
    field_name: str,
) -> str | None:
    """
    Normalize optional non-empty text.
    """

    if value is None:

        return None

    return _validated_text(
        value,
        field_name=field_name,
    )


def _validated_optional_count(
    value,
    *,
    field_name: str,
) -> int | None:
    """
    Require an optional non-negative integer.
    """

    if value is None:

        return None

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
    ):

        raise TypeError(
            f"{field_name} must be an integer."
        )

    if value < 0:

        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return value


def _validated_timestamp(
    value,
) -> datetime:
    """
    Require a timezone-aware timestamp.
    """

    if not isinstance(
        value,
        datetime,
    ):

        raise TypeError(
            "occurred_at must be a datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):

        raise ValueError(
            "occurred_at must include a timezone."
        )

    return value


@dataclass(
    frozen=True
)
class TrainingCoachUsageEvent:
    """
    Immutable factual record of one completed request.

    The record deliberately contains no activity payload,
    physiological data or generated interpretation.
    """

    user_id: str
    occurred_at: datetime
    status: TrainingCoachUsageStatus

    provider: str | None = None
    model: str | None = None
    error_code: str | None = None
    latency_ms: int | None = None
    remaining_user_requests: int | None = None
    remaining_global_requests: int | None = None

    usage_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    def __post_init__(
        self,
    ) -> None:

        object.__setattr__(
            self,
            "user_id",
            _validated_text(
                self.user_id,
                field_name="user_id",
            ),
        )

        object.__setattr__(
            self,
            "usage_id",
            _validated_text(
                self.usage_id,
                field_name="usage_id",
            ),
        )

        object.__setattr__(
            self,
            "occurred_at",
            _validated_timestamp(
                self.occurred_at
            ),
        )

        if not isinstance(
            self.status,
            TrainingCoachUsageStatus,
        ):

            raise TypeError(
                "status must be a "
                "TrainingCoachUsageStatus."
            )

        object.__setattr__(
            self,
            "provider",
            _validated_optional_text(
                self.provider,
                field_name="provider",
            ),
        )

        object.__setattr__(
            self,
            "model",
            _validated_optional_text(
                self.model,
                field_name="model",
            ),
        )

        object.__setattr__(
            self,
            "error_code",
            _validated_optional_text(
                self.error_code,
                field_name="error_code",
            ),
        )

        object.__setattr__(
            self,
            "latency_ms",
            _validated_optional_count(
                self.latency_ms,
                field_name="latency_ms",
            ),
        )

        object.__setattr__(
            self,
            "remaining_user_requests",
            _validated_optional_count(
                self.remaining_user_requests,
                field_name=(
                    "remaining_user_requests"
                ),
            ),
        )

        object.__setattr__(
            self,
            "remaining_global_requests",
            _validated_optional_count(
                self.remaining_global_requests,
                field_name=(
                    "remaining_global_requests"
                ),
            ),
        )

    @property
    def counts_toward_limit(
        self,
    ) -> bool:
        """
        Only a successfully generated result consumes
        the current daily allowance.
        """

        return (
            self.status
            is TrainingCoachUsageStatus
            .GENERATED
        )