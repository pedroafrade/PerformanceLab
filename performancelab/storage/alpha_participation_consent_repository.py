"""
PerformanceLab

Private alpha participation consent repository contract.
"""

from typing import (
    Protocol,
)

from performancelab.alpha_participation_consent import (
    AlphaParticipationConsent,
)


class AlphaParticipationConsentRepository(
    Protocol
):
    """
    Persistence contract for private alpha consent.
    """

    def latest(
        self,
        *,
        user_id: str,
        notice_version: str,
    ) -> AlphaParticipationConsent | None:
        """
        Return the latest consent for one notice version.
        """

        ...

    def save(
        self,
        consent: AlphaParticipationConsent,
    ) -> None:
        """
        Save an acceptance or its withdrawn state.
        """

        ...

    def list_for_user(
        self,
        user_id: str,
    ) -> tuple[
        AlphaParticipationConsent,
        ...,
    ]:
        """
        Return the consent history for one user.
        """

        ...