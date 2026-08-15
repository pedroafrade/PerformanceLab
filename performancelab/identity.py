"""
PerformanceLab

User identity models.
"""

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Literal,
)
from uuid import (
    uuid4,
)


UserRole = Literal[
    "athlete",
    "coach",
]


@dataclass(
    frozen=True
)
class ExternalIdentity:
    """
    Factual identity asserted by an external OIDC provider.

    This model does not grant access by itself. Provisioning
    and authorization remain separate application concerns.
    """

    issuer: str
    subject: str
    email: str
    email_verified: bool
    name: str | None = None

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize and validate the external identity.
        """

        if not isinstance(
            self.issuer,
            str,
        ):
            raise TypeError(
                "Identity issuer must be a string."
            )

        if not isinstance(
            self.subject,
            str,
        ):
            raise TypeError(
                "Identity subject must be a string."
            )

        if not isinstance(
            self.email,
            str,
        ):
            raise TypeError(
                "Identity email must be a string."
            )

        if not isinstance(
            self.email_verified,
            bool,
        ):
            raise TypeError(
                "email_verified must be a boolean."
            )

        normalized_issuer = (
            self.issuer.strip()
        )
        normalized_subject = (
            self.subject.strip()
        )
        normalized_email = (
            self.email
            .strip()
            .lower()
        )

        normalized_name = (
            self.name.strip()
            if isinstance(
                self.name,
                str,
            )
            and self.name.strip()
            else None
        )

        if not normalized_issuer:
            raise ValueError(
                "Identity issuer cannot be empty."
            )

        if not normalized_subject:
            raise ValueError(
                "Identity subject cannot be empty."
            )

        if (
            not normalized_email
            or "@" not in normalized_email
        ):
            raise ValueError(
                "Identity email must be valid."
            )

        if (
            self.name is not None
            and not isinstance(
                self.name,
                str,
            )
        ):
            raise TypeError(
                "Identity name must be a string or None."
            )

        object.__setattr__(
            self,
            "issuer",
            normalized_issuer,
        )
        object.__setattr__(
            self,
            "subject",
            normalized_subject,
        )
        object.__setattr__(
            self,
            "email",
            normalized_email,
        )
        object.__setattr__(
            self,
            "name",
            normalized_name,
        )

    @property
    def provider_key(
        self,
    ) -> tuple[str, str]:
        """
        Return the stable provider identity key.

        Email is intentionally excluded because an email
        address can change while issuer and subject remain
        stable.
        """

        return (
            self.issuer,
            self.subject,
        )


@dataclass
class User:
    """
    Represent a user who can access PerformanceLab.

    Athlete users are linked directly to their athlete profile.

    Coach users may later receive access to several athlete
    profiles through a separate access-control model.
    """

    email: str

    role: UserRole = "athlete"

    athlete_id: str | None = None

    user_id: str = field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Validate the user after initialization.
        """

        self.email = (
            self.email
            .strip()
            .lower()
        )

        if not self.email:
            raise ValueError(
                "User email cannot be empty."
            )

        if "@" not in self.email:
            raise ValueError(
                "User email must be valid."
            )

        if self.role not in (
            "athlete",
            "coach",
        ):
            raise ValueError(
                "User role must be "
                "'athlete' or 'coach'."
            )

        if (
            self.role == "athlete"
            and not self.athlete_id
        ):
            raise ValueError(
                "An athlete user must have "
                "an athlete_id."
            )

    @property
    def is_athlete(
        self,
    ) -> bool:
        """
        Return True when the user is an athlete.
        """

        return self.role == "athlete"

    @property
    def is_coach(
        self,
    ) -> bool:
        """
        Return True when the user is a coach.
        """

        return self.role == "coach"

    def __repr__(
        self,
    ) -> str:

        return (
            "User("
            f"email={self.email!r}, "
            f"role={self.role!r}, "
            f"user_id={self.user_id!r}"
            ")"
        )