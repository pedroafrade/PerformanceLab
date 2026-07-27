"""
PerformanceLab

JSON implementation of the user repository.
"""

import json
from pathlib import Path

from performancelab.identity import User


class JsonUserRepository:
    """
    Store each user in an individual JSON file.
    """

    def __init__(
        self,
        directory: str | Path = "data/users",
    ) -> None:
        self._directory = Path(directory)
        self._directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _path_for(self, user_id: str) -> Path:
        """
        Return the JSON path for a user.
        """
        return self._directory / f"{user_id}.json"

    def save(self, user: User) -> None:
        """
        Save or update a user.
        """
        path = self._path_for(user.user_id)

        data = {
            "id": user.user_id,
            "email": user.email,
            "role": user.role,
            "athlete_id": user.athlete_id,
        }

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    def get(self, user_id: str) -> User:
        """
        Return a user by ID.
        """
        path = self._path_for(user_id)

        if not path.exists():
            raise KeyError(
                f"User not found: {user_id}"
            )

        return self._load_from_path(path)

    def get_by_email(self, email: str) -> User:
        """
        Return a user by email address.

        Email comparison is case-insensitive.
        """
        normalized_email = email.strip().lower()

        for user in self.list():
            if user.email == normalized_email:
                return user

        raise KeyError(
            f"User not found: {normalized_email}"
        )

    def list(self) -> list[User]:
        """
        Return all stored users.
        """
        users = [
            self._load_from_path(path)
            for path in self._directory.glob("*.json")
        ]

        return sorted(
            users,
            key=lambda user: user.email,
        )

    def delete(self, user_id: str) -> None:
        """
        Delete a user by ID.
        """
        path = self._path_for(user_id)

        if not path.exists():
            raise KeyError(
                f"User not found: {user_id}"
            )

        path.unlink()

    def _load_from_path(self, path: Path) -> User:
        """
        Load a user from a JSON file.
        """
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return User(
            user_id=data["id"],
            email=data["email"],
            role=data["role"],
            athlete_id=data.get("athlete_id"),
        )