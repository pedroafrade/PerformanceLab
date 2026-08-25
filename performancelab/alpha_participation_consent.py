"""
PerformanceLab

Versioned consent for private alpha participation.
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


ALPHA_PARTICIPATION_CONSENT_VERSION = (
    "alpha-participation-consent-v1"
)


def _validated_text(
    value,
    *,
    field_name: str,
) -> str:
    """
    Require normalized non-empty text.
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
    *,
    field_name: str,
) -> datetime:
    """
    Require a timezone-aware timestamp.
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
class AlphaParticipationConsent:
    """
    Immutable acceptance of one private alpha notice.

    Withdrawal preserves the factual record while preventing
    continued participation under that consent.
    """

    user_id: str
    accepted_at: datetime

    notice_version: str = (
        ALPHA_PARTICIPATION_CONSENT_VERSION
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
            "notice_version",
            _validated_text(
                self.notice_version,
                field_name="notice_version",
            ),
        )

        object.__setattr__(
            self,
            "consent_id",
            _validated_text(
                self.consent_id,
                field_name="consent_id",
            ),
        )

        accepted_at = (
            _validated_timestamp(
                self.accepted_at,
                field_name="accepted_at",
            )
        )

        object.__setattr__(
            self,
            "accepted_at",
            accepted_at,
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

            if withdrawn_at < accepted_at:

                raise ValueError(
                    "withdrawn_at cannot be earlier "
                    "than accepted_at."
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
        Return the specific consent purpose.
        """

        return "private-alpha-participation"

    @property
    def is_active(
        self,
    ) -> bool:
        """
        Return whether consent remains active.
        """

        return (
            self.withdrawn_at
            is None
        )

    def permits_current_notice(
        self,
    ) -> bool:
        """
        Require active acceptance of the current notice.
        """

        return (
            self.is_active
            and self.notice_version
            == (
                ALPHA_PARTICIPATION_CONSENT_VERSION
            )
        )

    def withdraw(
        self,
        *,
        withdrawn_at: datetime,
    ):
        """
        Return a withdrawn immutable consent record.
        """

        if not self.is_active:

            return self

        return replace(
            self,
            withdrawn_at=withdrawn_at,
        )