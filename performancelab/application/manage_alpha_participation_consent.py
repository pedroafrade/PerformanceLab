"""
PerformanceLab

Manage versioned private alpha participation consent.
"""

from datetime import (
    datetime,
    timezone,
)
from typing import (
    Callable,
)

from performancelab.alpha_participation_consent import (
    ALPHA_PARTICIPATION_CONSENT_VERSION,
    AlphaParticipationConsent,
)
from performancelab.storage.alpha_participation_consent_repository import (
    AlphaParticipationConsentRepository,
)


def current_utc_time() -> datetime:
    """
    Return the current timezone-aware UTC time.
    """

    return datetime.now(
        timezone.utc
    )


class ManageAlphaParticipationConsent:
    """
    Accept, inspect and withdraw private alpha consent.
    """

    def __init__(
        self,
        *,
        repository: (
            AlphaParticipationConsentRepository
        ),
        clock: Callable[
            [],
            datetime,
        ] = current_utc_time,
    ) -> None:

        if not callable(
            clock
        ):

            raise TypeError(
                "clock must be callable."
            )

        self._repository = repository
        self._clock = clock

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

    def current(
        self,
        *,
        user_id: str,
    ) -> AlphaParticipationConsent | None:
        """
        Return the latest state for the current notice.
        """

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        return self._repository.latest(
            user_id=normalized_user_id,
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )

    def is_permitted(
        self,
        *,
        user_id: str,
    ) -> bool:
        """
        Return whether private alpha access is permitted.
        """

        consent = self.current(
            user_id=user_id
        )

        return (
            consent is not None
            and consent.permits_current_notice()
        )

    def accept(
        self,
        *,
        user_id: str,
    ) -> AlphaParticipationConsent:
        """
        Accept the current private alpha notice.

        Repeated acceptance preserves an existing active
        consent.
        """

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        existing = self.current(
            user_id=normalized_user_id
        )

        if (
            existing is not None
            and existing.permits_current_notice()
        ):

            return existing

        accepted = AlphaParticipationConsent(
            user_id=normalized_user_id,
            accepted_at=self._clock(),
            notice_version=(
                ALPHA_PARTICIPATION_CONSENT_VERSION
            ),
        )

        self._repository.save(
            accepted
        )

        return accepted

    def withdraw(
        self,
        *,
        user_id: str,
    ) -> AlphaParticipationConsent | None:
        """
        Withdraw the current active consent.
        """

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        existing = self.current(
            user_id=normalized_user_id
        )

        if (
            existing is None
            or not existing.is_active
        ):

            return existing

        withdrawn = existing.withdraw(
            withdrawn_at=self._clock()
        )

        self._repository.save(
            withdrawn
        )

        return withdrawn