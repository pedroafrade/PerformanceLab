"""
PerformanceLab

Athlete access authorization model.
"""

from dataclasses import (
    dataclass,
)
from typing import (
    Literal,
)


AthleteAccessPermission = Literal[
    "owner",
    "coach",
]


@dataclass(
    frozen=True
)
class AthleteAccessGrant:
    """
    Explicit authorization for a user to access an athlete.

    A grant states only who may access which athlete and in
    what capacity. It does not authenticate the user.
    """

    user_id: str
    athlete_id: str
    permission: AthleteAccessPermission = "owner"

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize and validate the access grant.
        """

        for field_name in (
            "user_id",
            "athlete_id",
        ):

            value = getattr(
                self,
                field_name,
            )

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

            object.__setattr__(
                self,
                field_name,
                normalized_value,
            )

        if self.permission not in (
            "owner",
            "coach",
        ):
            raise ValueError(
                "permission must be "
                "'owner' or 'coach'."
            )

    @property
    def grant_key(
        self,
    ) -> tuple[str, str]:
        """
        Return the stable authorization key.
        """

        return (
            self.user_id,
            self.athlete_id,
        )

    @property
    def is_owner(
        self,
    ) -> bool:
        """
        Return whether this is owner access.
        """

        return (
            self.permission
            == "owner"
        )

    @property
    def is_coach(
        self,
    ) -> bool:
        """
        Return whether this is coach access.
        """

        return (
            self.permission
            == "coach"
        )