"""
PerformanceLab

Private alpha invitation repository contract.
"""

from typing import (
    Protocol,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)


class AlphaInvitationRepository(
    Protocol
):
    """
    Persistence operations for private alpha invitations.
    """

    def get(
        self,
        invitation_id: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by ID.
        """

        ...

    def get_by_email(
        self,
        email: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by normalized email.
        """

        ...

    def save(
        self,
        invitation: AlphaInvitation,
    ) -> None:
        """
        Save or update an invitation.
        """

        ...

    def list(
        self,
    ) -> list[
        AlphaInvitation
    ]:
        """
        Return every invitation.
        """

        ...

    def delete(
        self,
        invitation_id: str,
    ) -> None:
        """
        Delete an invitation.
        """

        ...