"""
PerformanceLab

Private alpha invitation model.
"""

from dataclasses import (
    dataclass,
    field,
    replace,
)
from uuid import (
    uuid4,
)

from performancelab.identity import (
    UserRole,
)


@dataclass(
    frozen=True
)
class AlphaInvitation:
    """
    Invitation required to provision a private alpha user.
    """

    email: str
    role: UserRole = "athlete"
    athlete_id: str | None = None
    invitation_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )
    claimed_by_user_id: str | None = None

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize and validate the invitation.
        """

        if not isinstance(
            self.email,
            str,
        ):
            raise TypeError(
                "Invitation email must be a string."
            )

        normalized_email = (
            self.email
            .strip()
            .lower()
        )

        if (
            not normalized_email
            or "@" not in normalized_email
        ):
            raise ValueError(
                "Invitation email must be valid."
            )

        if self.role not in (
            "athlete",
            "coach",
        ):
            raise ValueError(
                "Invitation role must be "
                "'athlete' or 'coach'."
            )

        if not isinstance(
            self.invitation_id,
            str,
        ) or not self.invitation_id.strip():
            raise ValueError(
                "invitation_id cannot be empty."
            )

        normalized_athlete_id = (
            self.athlete_id.strip()
            if isinstance(
                self.athlete_id,
                str,
            )
            and self.athlete_id.strip()
            else None
        )

        if (
            self.athlete_id is not None
            and not isinstance(
                self.athlete_id,
                str,
            )
        ):
            raise TypeError(
                "athlete_id must be a string or None."
            )

        if (
            self.role == "athlete"
            and normalized_athlete_id is None
        ):
            raise ValueError(
                "An athlete invitation must have "
                "an athlete_id."
            )

        normalized_claimed_user = (
            self.claimed_by_user_id.strip()
            if isinstance(
                self.claimed_by_user_id,
                str,
            )
            and self.claimed_by_user_id.strip()
            else None
        )

        if (
            self.claimed_by_user_id is not None
            and not isinstance(
                self.claimed_by_user_id,
                str,
            )
        ):
            raise TypeError(
                "claimed_by_user_id must be "
                "a string or None."
            )

        object.__setattr__(
            self,
            "email",
            normalized_email,
        )
        object.__setattr__(
            self,
            "athlete_id",
            normalized_athlete_id,
        )
        object.__setattr__(
            self,
            "invitation_id",
            self.invitation_id.strip(),
        )
        object.__setattr__(
            self,
            "claimed_by_user_id",
            normalized_claimed_user,
        )

    @property
    def is_claimed(
        self,
    ) -> bool:
        """
        Return whether the invitation has been claimed.
        """

        return (
            self.claimed_by_user_id
            is not None
        )

    def claim(
        self,
        user_id: str,
    ):
        """
        Return an invitation claimed by one internal user.
        """

        if not isinstance(
            user_id,
            str,
        ):
            raise TypeError(
                "user_id must be a string."
            )

        normalized_user_id = (
            user_id.strip()
        )

        if not normalized_user_id:
            raise ValueError(
                "user_id cannot be empty."
            )

        if (
            self.claimed_by_user_id
            == normalized_user_id
        ):
            return self

        if self.is_claimed:
            raise ValueError(
                "Invitation has already been "
                "claimed by another user."
            )

        return replace(
            self,
            claimed_by_user_id=(
                normalized_user_id
            ),
        )