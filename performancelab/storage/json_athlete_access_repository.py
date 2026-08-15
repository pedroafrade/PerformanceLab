"""
PerformanceLab

JSON athlete access repository.
"""

import hashlib
import json

from pathlib import (
    Path,
)

from performancelab.athlete_access import (
    AthleteAccessGrant,
)


class JsonAthleteAccessRepository:
    """
    Store athlete access grants in individual JSON files.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/athlete_access"
        ),
    ) -> None:

        self._directory = Path(
            directory
        )

        self._directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    @staticmethod
    def _normalized_key(
        user_id: str,
        athlete_id: str,
    ) -> tuple[str, str]:
        """
        Normalize and validate a grant key.
        """

        normalized_values = []

        for field_name, value in (
            (
                "user_id",
                user_id,
            ),
            (
                "athlete_id",
                athlete_id,
            ),
        ):

            if not isinstance(
                value,
                str,
            ):
                raise TypeError(
                    f"{field_name} must be a string."
                )

            normalized_value = (
                value.strip()
            )

            if not normalized_value:
                raise ValueError(
                    f"{field_name} cannot be empty."
                )

            normalized_values.append(
                normalized_value
            )

        return (
            normalized_values[0],
            normalized_values[1],
        )

    def _path_for(
        self,
        user_id: str,
        athlete_id: str,
    ) -> Path:
        """
        Return a filesystem-safe path for one grant.
        """

        grant_key = (
            self._normalized_key(
                user_id,
                athlete_id,
            )
        )

        serialized_key = json.dumps(
            grant_key,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        digest = hashlib.sha256(
            serialized_key.encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            self._directory
            / f"{digest}.json"
        )

    def get(
        self,
        user_id: str,
        athlete_id: str,
    ) -> AthleteAccessGrant:
        """
        Return one explicit access grant.
        """

        path = self._path_for(
            user_id,
            athlete_id,
        )

        if not path.exists():

            raise KeyError(
                "Athlete access grant "
                "does not exist."
            )

        return self._load_from_path(
            path
        )

    def save(
        self,
        grant: AthleteAccessGrant,
    ) -> None:
        """
        Save a grant without silently changing permission.
        """

        if not isinstance(
            grant,
            AthleteAccessGrant,
        ):
            raise TypeError(
                "grant must be an "
                "AthleteAccessGrant."
            )

        path = self._path_for(
            grant.user_id,
            grant.athlete_id,
        )

        if path.exists():

            existing = (
                self._load_from_path(
                    path
                )
            )

            if existing != grant:

                raise ValueError(
                    "Athlete access permission "
                    "cannot be changed silently."
                )

            return

        data = {
            "version": 1,
            "user_id": grant.user_id,
            "athlete_id": grant.athlete_id,
            "permission": (
                grant.permission
            ),
        }

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_path.replace(
            path
        )

    def delete(
        self,
        user_id: str,
        athlete_id: str,
    ) -> None:
        """
        Delete one access grant.
        """

        path = self._path_for(
            user_id,
            athlete_id,
        )

        if not path.exists():

            raise KeyError(
                "Athlete access grant "
                "does not exist."
            )

        path.unlink()

    def list_for_user(
        self,
        user_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return every grant belonging to one user.
        """

        normalized_user_id, _ = (
            self._normalized_key(
                user_id,
                "placeholder-athlete",
            )
        )

        return [
            grant
            for grant in self.list()
            if (
                grant.user_id
                == normalized_user_id
            )
        ]

    def list_for_athlete(
        self,
        athlete_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return every grant for one athlete.
        """

        _, normalized_athlete_id = (
            self._normalized_key(
                "placeholder-user",
                athlete_id,
            )
        )

        return [
            grant
            for grant in self.list()
            if (
                grant.athlete_id
                == normalized_athlete_id
            )
        ]

    def list(
        self,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return every access grant.
        """

        grants = [
            self._load_from_path(
                path
            )
            for path
            in self._directory.glob(
                "*.json"
            )
        ]

        return sorted(
            grants,
            key=lambda grant: (
                grant.user_id,
                grant.athlete_id,
            ),
        )

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> AthleteAccessGrant:
        """
        Load and validate one persisted grant.
        """

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        if data.get(
            "version"
        ) != 1:
            raise ValueError(
                "Unsupported athlete access "
                "grant version."
            )

        return AthleteAccessGrant(
            user_id=data["user_id"],
            athlete_id=(
                data["athlete_id"]
            ),
            permission=(
                data["permission"]
            ),
        )