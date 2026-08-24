"""
PerformanceLab

Training Coach consent repository contract.
"""

from typing import (
    Protocol,
)

from performancelab.training_coach_consent import (
    TrainingCoachConsent,
)


class TrainingCoachConsentRepository(
    Protocol
):
    """
    Persistence contract for versioned Training Coach consent.
    """

    def latest(
        self,
        *,
        user_id: str,
        policy_version: str,
    ) -> TrainingCoachConsent | None:
        """
        Return the latest consent state for one policy version.
        """

        ...

    def save(
        self,
        consent: TrainingCoachConsent,
    ) -> None:
        """
        Save a new consent or its withdrawn state.
        """

        ...

    def list_for_user(
        self,
        user_id: str,
    ) -> tuple[
        TrainingCoachConsent,
        ...,
    ]:
        """
        Return the complete consent history for one user.
        """

        ...