"""
PerformanceLab

Athlete authorization service.
"""

from collections.abc import (
    Iterable,
)
from dataclasses import (
    dataclass,
)

from performancelab.athlete_access import (
    AthleteAccessGrant,
    AthleteAccessPermission,
)
from performancelab.storage.athlete_access_repository import (
    AthleteAccessRepository,
)


@dataclass(
    frozen=True
)
class AthleteAuthorizationDecision:
    """
    Immutable result of an athlete access decision.
    """

    allowed: bool
    user_id: str
    athlete_id: str
    permission: AthleteAccessPermission | None
    reason: str


class AthleteAuthorizationService:
    """
    Authorize explicit user access to athlete resources.

    User roles, emails and session state do not grant access.
    Only a persisted AthleteAccessGrant is authoritative.
    """

    def __init__(
        self,
        repository: AthleteAccessRepository,
    ) -> None:

        self._repository = repository

    def decide(
        self,
        *,
        user_id: str,
        athlete_id: str,
        allowed_permissions: Iterable[
            AthleteAccessPermission
        ] = (
            "owner",
            "coach",
        ),
    ) -> AthleteAuthorizationDecision:
        """
        Return an explicit authorization decision.
        """

        normalized_user_id = (
            self._required_identifier(
                user_id,
                field="user_id",
            )
        )

        normalized_athlete_id = (
            self._required_identifier(
                athlete_id,
                field="athlete_id",
            )
        )

        permissions = (
            self._permissions(
                allowed_permissions
            )
        )

        try:

            grant = self._repository.get(
                normalized_user_id,
                normalized_athlete_id,
            )

        except KeyError:

            return AthleteAuthorizationDecision(
                allowed=False,
                user_id=normalized_user_id,
                athlete_id=(
                    normalized_athlete_id
                ),
                permission=None,
                reason="grant_not_found",
            )

        if (
            grant.permission
            not in permissions
        ):

            return AthleteAuthorizationDecision(
                allowed=False,
                user_id=normalized_user_id,
                athlete_id=(
                    normalized_athlete_id
                ),
                permission=(
                    grant.permission
                ),
                reason=(
                    "permission_not_allowed"
                ),
            )

        return AthleteAuthorizationDecision(
            allowed=True,
            user_id=normalized_user_id,
            athlete_id=(
                normalized_athlete_id
            ),
            permission=grant.permission,
            reason="authorized",
        )

    def require_access(
        self,
        *,
        user_id: str,
        athlete_id: str,
        allowed_permissions: Iterable[
            AthleteAccessPermission
        ] = (
            "owner",
            "coach",
        ),
    ) -> AthleteAccessGrant:
        """
        Return the grant or raise PermissionError.
        """

        decision = self.decide(
            user_id=user_id,
            athlete_id=athlete_id,
            allowed_permissions=(
                allowed_permissions
            ),
        )

        if not decision.allowed:

            raise PermissionError(
                "User is not authorized to access "
                f"athlete {decision.athlete_id!r}: "
                f"{decision.reason}."
            )

        return self._repository.get(
            decision.user_id,
            decision.athlete_id,
        )

    def accessible_athlete_ids(
        self,
        *,
        user_id: str,
        allowed_permissions: Iterable[
            AthleteAccessPermission
        ] = (
            "owner",
            "coach",
        ),
    ) -> tuple[str, ...]:
        """
        Return athlete IDs explicitly accessible to a user.
        """

        normalized_user_id = (
            self._required_identifier(
                user_id,
                field="user_id",
            )
        )

        permissions = (
            self._permissions(
                allowed_permissions
            )
        )

        grants = (
            self._repository
            .list_for_user(
                normalized_user_id
            )
        )

        return tuple(
            grant.athlete_id
            for grant in grants
            if (
                grant.permission
                in permissions
            )
        )

    @staticmethod
    def _required_identifier(
        value,
        *,
        field: str,
    ) -> str:
        """
        Validate and normalize one identifier.
        """

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field} must be a string."
            )

        normalized_value = (
            value.strip()
        )

        if not normalized_value:
            raise ValueError(
                f"{field} cannot be empty."
            )

        return normalized_value

    @staticmethod
    def _permissions(
        values: Iterable[
            AthleteAccessPermission
        ],
    ) -> tuple[
        AthleteAccessPermission,
        ...
    ]:
        """
        Validate the accepted permission collection.
        """

        if isinstance(
            values,
            str,
        ):
            raise TypeError(
                "allowed_permissions must be "
                "an iterable, not a string."
            )

        try:

            permissions = tuple(
                values
            )

        except TypeError as error:

            raise TypeError(
                "allowed_permissions must be iterable."
            ) from error

        if not permissions:

            raise ValueError(
                "allowed_permissions cannot be empty."
            )

        for permission in permissions:

            if permission not in (
                "owner",
                "coach",
            ):
                raise ValueError(
                    "Unsupported athlete access "
                    f"permission: {permission!r}."
                )

        return permissions