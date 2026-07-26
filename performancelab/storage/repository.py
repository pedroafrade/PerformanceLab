"""
PerformanceLab

Athlete repository interface.

Defines the persistence contract used to load and save athletes.
"""

from pathlib import Path
from typing import Protocol

from performancelab.athlete import Athlete


class AthleteRepository(Protocol):
    """
    Persistence interface for Athlete objects.

    Implementations may store athletes in JSON files,
    databases or remote services.
    """

    @property
    def path(self) -> Path:
        """
        Return the storage location used by the repository.
        """
        ...

    def exists(self) -> bool:
        """
        Return True when stored athlete data exists.
        """
        ...

    def load(self) -> Athlete:
        """
        Load and return the stored athlete.

        Raises:
            FileNotFoundError:
                If no stored athlete exists.
        """
        ...

    def save(
        self,
        athlete: Athlete,
    ) -> Path:
        """
        Persist an athlete and return the storage path.
        """
        ...