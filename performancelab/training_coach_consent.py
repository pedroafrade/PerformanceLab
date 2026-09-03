"""
PerformanceLab

Versioned consent for Training Coach data processing.
"""

from dataclasses import (
    dataclass,
    field,
    replace,
)
from datetime import (
    datetime,
)
from uuid import (
    uuid4,
)


TRAINING_COACH_CONSENT_VERSION = (
    "training-coach-consent-v2"
)


def _validated_timestamp(
    value,
    *,
    field_name: str,
) -> datetime:
    """
    Require an explicit timezone for consent timestamps.
    """

    if not isinstance(
        value,
        datetime,
    ):

        raise TypeError(
            f"{field_name} must be a datetime."
        )

    if (
        value.tzinfo is None
        or value.utcoffset() is None
    ):

        raise ValueError(
            f"{field_name} must include a timezone."
        )

    return value


@dataclass(
    frozen=True
)
class TrainingCoachConsent:
    """
    Immutable, versioned consent granted by one internal user.

    Version 2 covers requested activity interpretations and automatic Daily
    Brief processing together. Version 1 was manual-only and is not upgraded
    silently. One withdrawal blocks both workflows.

    Withdrawal preserves the historical consent record while
    preventing any further Training Coach generation.
    """

    user_id: str
    granted_at: datetime

    policy_version: str = (
        TRAINING_COACH_CONSENT_VERSION
    )

    withdrawn_at: datetime | None = None

    consent_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    def __post_init__(
        self,
    ) -> None:

        for field_name in (
            "user_id",
            "policy_version",
            "consent_id",
        ):

            value = getattr(
                self,
                field_name,
            )

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

            object.__setattr__(
                self,
                field_name,
                normalized_value,
            )

        granted_at = (
            _validated_timestamp(
                self.granted_at,
                field_name="granted_at",
            )
        )

        object.__setattr__(
            self,
            "granted_at",
            granted_at,
        )

        if (
            self.withdrawn_at
            is not None
        ):

            withdrawn_at = (
                _validated_timestamp(
                    self.withdrawn_at,
                    field_name=(
                        "withdrawn_at"
                    ),
                )
            )

            if (
                withdrawn_at
                < granted_at
            ):

                raise ValueError(
                    "withdrawn_at cannot be earlier "
                    "than granted_at."
                )

            object.__setattr__(
                self,
                "withdrawn_at",
                withdrawn_at,
            )

    @property
    def purpose(
        self,
    ) -> str:
        """
        Return the specific processing purpose.
        """

        return "training-coach"

    @property
    def is_active(
        self,
    ) -> bool:
        """
        Return whether consent has not been withdrawn.
        """

        return (
            self.withdrawn_at
            is None
        )

    def permits_current_policy(
        self,
    ) -> bool:
        """
        Require active consent for the current policy version.
        """

        return (
            self.is_active
            and self.policy_version
            == (
                TRAINING_COACH_CONSENT_VERSION
            )
        )

    def withdraw(
        self,
        *,
        withdrawn_at: datetime,
    ):
        """
        Return a withdrawn version of this consent.

        Repeated withdrawal returns the same immutable record.
        """

        if not self.is_active:

            return self

        return replace(
            self,
            withdrawn_at=withdrawn_at,
        )
