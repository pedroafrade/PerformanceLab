"""
PerformanceLab

Manage versioned Training Coach consent.
"""

from datetime import (
    datetime,
    timezone,
)
from typing import (
    Callable,
)

from performancelab.storage.training_coach_consent_repository import (
    TrainingCoachConsentRepository,
)
from performancelab.training_coach_consent import (
    TRAINING_COACH_CONSENT_VERSION,
    TrainingCoachConsent,
)


def current_utc_time() -> datetime:
    """
    Return the current timezone-aware UTC time.
    """

    return datetime.now(
        timezone.utc
    )


class ManageTrainingCoachConsent:
    """
    Grant, inspect and withdraw Training Coach consent.

    Consent belongs to the authenticated internal user and is
    valid only for the current policy version.
    """

    def __init__(
        self,
        *,
        repository: TrainingCoachConsentRepository,
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
    ) -> TrainingCoachConsent | None:
        """
        Return the latest state for the current policy.
        """

        normalized_user_id = (
            self._normalized_user_id(
                user_id
            )
        )

        return self._repository.latest(
            user_id=normalized_user_id,
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )

    def is_permitted(
        self,
        *,
        user_id: str,
    ) -> bool:
        """
        Return whether Training Coach generation is permitted.
        """

        consent = self.current(
            user_id=user_id
        )

        return (
            consent is not None
            and consent.permits_current_policy()
        )

    def grant(
        self,
        *,
        user_id: str,
    ) -> TrainingCoachConsent:
        """
        Grant consent for the current policy version.

        Repeated granting preserves an existing active consent.
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
            and existing.permits_current_policy()
        ):

            return existing

        granted = TrainingCoachConsent(
            user_id=normalized_user_id,
            granted_at=self._clock(),
            policy_version=(
                TRAINING_COACH_CONSENT_VERSION
            ),
        )

        self._repository.save(
            granted
        )

        return granted

    def withdraw(
        self,
        *,
        user_id: str,
    ) -> TrainingCoachConsent | None:
        """
        Withdraw the current active consent.

        If no active consent exists, no new record is created.
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