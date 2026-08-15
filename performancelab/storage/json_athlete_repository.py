"""
PerformanceLab

JSON athlete repository.

Provides Athlete persistence using one JSON file per athlete.
"""

from pathlib import Path

from performancelab.athlete import Athlete

from .json import (
    load_athlete,
    save_athlete,
)


class JsonAthleteRepository:
    """
    Store and retrieve athletes from a directory of JSON files.

    Each athlete is stored in a file named ``<athlete_id>.json``.
    The temporary ``load()`` and parameterless ``exists()`` methods keep the
    current single-athlete application working during the migration.
    """

    def __init__(self, directory: Path):
        # During the transition, app.py may still pass
        # ``data/athletes/athlete.json`` instead of ``data/athletes``.
        # Normalise both forms to the athletes directory.
        self.directory = (
            directory.parent
            if directory.suffix.lower() == ".json"
            else directory
        )

    def _path_for(self, athlete_id: str) -> Path:
        """Return the JSON path for an athlete ID."""
        return self.directory / f"{athlete_id}.json"

    def _athlete_files(self) -> list[Path]:
        """Return all athlete JSON files in a stable order."""
        if not self.directory.exists():
            return []

        return sorted(self.directory.glob("*.json"))

    def exists(self, athlete_id: str | None = None) -> bool:
        """
        Return whether an athlete exists.

        Without an ID, return True when the repository contains at least one
        athlete. This temporary behaviour supports the current app.py.
        """
        if athlete_id is None:
            return bool(self._athlete_files())

        return self._path_for(athlete_id).exists()

    def load(self) -> Athlete:
        """
        Load the only athlete in the repository.

        This is a temporary compatibility method for the single-athlete app.
        Use ``get(athlete_id)`` once athlete selection or authentication exists.
        """
        files = self._athlete_files()

        if not files:
            raise FileNotFoundError(
                f"No athlete JSON files found in {self.directory}"
            )

        if len(files) > 1:
            raise RuntimeError(
                "More than one athlete exists. "
                "Use get(athlete_id) instead of load()."
            )

        return load_athlete(files[0])

    def get(self, athlete_id: str) -> Athlete:
        """Load an athlete by ID."""
        return load_athlete(
            self._path_for(athlete_id)
        )

    def list(self) -> list[Athlete]:
        """Load and return all athletes."""
        return [
            load_athlete(path)
            for path in self._athlete_files()
        ]

    def save(
        self,
        athlete: Athlete,
    ) -> None:
        """
        Save an athlete using its persistent ID as the
        filename.
        """

        target_path = self._path_for(
            athlete.athlete_id
        )

        save_athlete(
            athlete,
            target_path,
        )

        # Remove the old single-athlete filename after a
        # successful save.
        legacy_path = (
            self.directory
            / "athlete.json"
        )

        if (
            legacy_path != target_path
            and legacy_path.exists()
        ):
            legacy_path.unlink()

    def delete(self, athlete_id: str) -> None:
        """Delete an athlete by ID."""
        path = self._path_for(athlete_id)

        if not path.exists():
            raise FileNotFoundError(
                f"Athlete {athlete_id!r} does not exist"
            )

        path.unlink()

    def __repr__(self) -> str:
        return (
            "JsonAthleteRepository("
            f"directory={self.directory!r})"
        )