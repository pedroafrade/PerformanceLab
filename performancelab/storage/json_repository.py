"""
PerformanceLab

JSON athlete repository.

Provides Athlete persistence using a JSON file.
"""

from pathlib import Path

from performancelab.athlete import Athlete

from .json import (
    load_athlete,
    save_athlete,
)


class JsonAthleteRepository:
    """
    Store and retrieve an Athlete using a JSON file.
    """

    def __init__(
        self,
        path: str | Path,
    ) -> None:
        self._path = Path(path)

    @property
    def path(self) -> Path:
        """
        Return the JSON file used by the repository.
        """
        return self._path

    def exists(self) -> bool:
        """
        Return True when the JSON file exists.
        """
        return self._path.exists()

    def load(self) -> Athlete:
        """
        Load an Athlete from the configured JSON file.
        """
        return load_athlete(
            self._path,
        )

    def save(
        self,
        athlete: Athlete,
    ) -> Path:
        """
        Save an Athlete to the configured JSON file.
        """
        return save_athlete(
            athlete,
            self._path,
        )

    def __repr__(self) -> str:
        return (
            "JsonAthleteRepository("
            f"path={self._path!r})"
        )