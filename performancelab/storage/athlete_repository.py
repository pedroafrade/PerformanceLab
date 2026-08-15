"""
PerformanceLab

Athlete repository interface.

Defines the persistence contract used to load and save
multiple athletes.
"""

from typing import (
    Protocol,
    runtime_checkable,
)

from performancelab.athlete import (
    Athlete,
)


@runtime_checkable
class AthleteRepository(
    Protocol
):
    """
    Persistence interface for Athlete aggregates.

    Implementations may store athletes in JSON files,
    databases or remote services.

    Authorization must be completed before an athlete ID
    is passed to this repository. Listing every athlete is
    reserved for explicitly authorized application flows.
    """

    def get(
        self,
        athlete_id: str,
    ) -> Athlete:
        """
        Return the athlete identified by athlete_id.

        Raises:
            FileNotFoundError:
                If the athlete does not exist.
        """
        ...

    def list(
        self,
    ) -> list[Athlete]:
        """
        Return every stored athlete.

        This operation must only be used by an explicitly
        authorized application flow.
        """
        ...

    def save(
        self,
        athlete: Athlete,
    ) -> None:
        """
        Persist the complete athlete aggregate.
        """
        ...

    def delete(
        self,
        athlete_id: str,
    ) -> None:
        """
        Delete the athlete identified by athlete_id.

        Raises:
            FileNotFoundError:
                If the athlete does not exist.
        """
        ...