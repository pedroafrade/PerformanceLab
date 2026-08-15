"""
PerformanceLab

Athlete access repository contract.
"""

from typing import (
    Protocol,
)

from performancelab.athlete_access import (
    AthleteAccessGrant,
)


class AthleteAccessRepository(
    Protocol
):
    """
    Persistence operations for athlete access grants.
    """

    def get(
        self,
        user_id: str,
        athlete_id: str,
    ) -> AthleteAccessGrant:
        """
        Return one explicit access grant.
        """

        ...

    def save(
        self,
        grant: AthleteAccessGrant,
    ) -> None:
        """
        Save a grant without silently changing permission.
        """

        ...

    def delete(
        self,
        user_id: str,
        athlete_id: str,
    ) -> None:
        """
        Delete one access grant.
        """

        ...

    def list_for_user(
        self,
        user_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return all grants belonging to one user.
        """

        ...

    def list_for_athlete(
        self,
        athlete_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return all grants for one athlete.
        """

        ...

    def list(
        self,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return every access grant.
        """

        ...