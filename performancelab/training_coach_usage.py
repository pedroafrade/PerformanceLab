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