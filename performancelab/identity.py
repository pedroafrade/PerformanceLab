"""
PerformanceLab

User identity models.
"""

from dataclasses import dataclass, field
from typing import Literal
from uuid import uuid4


UserRole = Literal["athlete", "coach"]


@dataclass
class User:
    """
    Represent a user who can access PerformanceLab.

    Athlete users are linked directly to their athlete profile.

    Coach users may later receive access to several athlete profiles through
    a separate access-control model.
    """

    email: str

    role: UserRole = "athlete"

    athlete_id: str | None = None

    user_id: str = field(
        default_factory=lambda: str(uuid4())
    )

    def __post_init__(self) -> None:
        """
        Validate the user after initialization.
        """
        self.email = self.email.strip().lower()

        if not self.email:
            raise ValueError(
                "User email cannot be empty."
            )

        if "@" not in self.email:
            raise ValueError(
                "User email must be valid."
            )

        if self.role not in ("athlete", "coach"):
            raise ValueError(
                "User role must be 'athlete' or 'coach'."
            )

        if self.role == "athlete" and not self.athlete_id:
            raise ValueError(
                "An athlete user must have an athlete_id."
            )

    @property
    def is_athlete(self) -> bool:
        """
        Return True when the user is an athlete.
        """
        return self.role == "athlete"

    @property
    def is_coach(self) -> bool:
        """
        Return True when the user is a coach.
        """
        return self.role == "coach"

    def __repr__(self) -> str:
        return (
            "User("
            f"email={self.email!r}, "
            f"role={self.role!r}, "
            f"user_id={self.user_id!r}"
            ")"
        )