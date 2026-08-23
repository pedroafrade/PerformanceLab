"""
PerformanceLab

Provision invited external user application use case.
"""
from contextlib import (
    nullcontext,
)

from dataclasses import (
    dataclass,
)

from typing import (
    Callable,
    ContextManager,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.identity import (
    ExternalIdentity,
    ExternalIdentityLink,
    User,
)
from performancelab.storage.alpha_invitation_repository import (
    AlphaInvitationRepository,
)
from performancelab.storage.athlete_access_repository import (
    AthleteAccessRepository,
)
from performancelab.storage.athlete_repository import (
    AthleteRepository,
)
from performancelab.storage.external_identity_repository import (
    ExternalIdentityRepository,
)
from performancelab.storage.user_repository import (
    UserRepository,
)


@dataclass(
    frozen=True
)
class ProvisionInvitedUserResult:
    """
    Result of resolving or provisioning an external user.
    """

    user: User
    created: bool
    invitation: AlphaInvitation | None
    access_grant: AthleteAccessGrant | None


class ProvisionInvitedUser:
    """
    Resolve or provision a verified invited external user.

    This local implementation validates every business rule
    before writing. PostgreSQL transactions will later replace
    the compensating rollback used for infrastructure failures.
    """

    def __init__(
        self,
        *,
        user_repository: UserRepository,
        identity_repository: ExternalIdentityRepository,
        invitation_repository: AlphaInvitationRepository,
        access_repository: AthleteAccessRepository,
        athlete_repository: AthleteRepository,
        transaction_factory: Callable[
            [],
            ContextManager,
        ] = nullcontext,
    ) -> None:

        self._user_repository = (
            user_repository
        )
        self._identity_repository = (
            identity_repository
        )
        self._invitation_repository = (
            invitation_repository
        )
        self._access_repository = (
            access_repository
        )
        self._athlete_repository = (
            athlete_repository
        )
        if not callable(
            transaction_factory
        ):
            raise TypeError(
                "transaction_factory must be callable."
            )

        self._transaction_factory = (
            transaction_factory
        )

    def execute(
        self,
        identity: ExternalIdentity,
    ) -> ProvisionInvitedUserResult:
        """
        Resolve or provision a user as one complete operation.
        """

        with self._transaction_factory():

            return self._execute(
                identity
            )

    def _execute(
        self,
        identity: ExternalIdentity,
    ) -> ProvisionInvitedUserResult:
        """
        Resolve an existing link or provision an invited user.
        """

        if not isinstance(
            identity,
            ExternalIdentity,
        ):
            raise TypeError(
                "identity must be an ExternalIdentity."
            )

        if not identity.email_verified:
            raise PermissionError(
                "A verified external email is required."
            )

        existing_result = (
            self._existing_identity_result(
                identity
            )
        )

        if existing_result is not None:
            return existing_result

        try:

            invitation = (
                self._invitation_repository
                .get_by_email(
                    identity.email
                )
            )

        except KeyError as error:

            raise PermissionError(
                "This email is not invited "
                "to the private alpha."
            ) from error

        if invitation.is_claimed:
            raise RuntimeError(
                "The invitation is already claimed "
                "but has no external identity link."
            )

        if invitation.role != "athlete":
            raise PermissionError(
                "Coach accounts are disabled "
                "for the first private alpha."
            )

        athlete_id = (
            invitation.athlete_id
        )

        if athlete_id is None:
            raise RuntimeError(
                "The athlete invitation has no athlete."
            )

        try:

            self._athlete_repository.get(
                athlete_id
            )

        except FileNotFoundError as error:

            raise RuntimeError(
                "The invited athlete profile "
                "does not exist."
            ) from error

        user, created = (
            self._user_for_invitation(
                invitation
            )
        )

        link = (
            ExternalIdentityLink
            .from_identity(
                identity,
                user_id=user.user_id,
            )
        )

        access_grant = AthleteAccessGrant(
            user_id=user.user_id,
            athlete_id=athlete_id,
            permission="owner",
        )

        self._validate_existing_access(
            access_grant
        )

        claimed_invitation = (
            invitation.claim(
                user.user_id
            )
        )

        self._persist(
            user=user,
            created=created,
            link=link,
            access_grant=access_grant,
            invitation=invitation,
            claimed_invitation=(
                claimed_invitation
            ),
        )

        return ProvisionInvitedUserResult(
            user=user,
            created=created,
            invitation=(
                claimed_invitation
            ),
            access_grant=(
                access_grant
            ),
        )

    def _existing_identity_result(
        self,
        identity: ExternalIdentity,
    ) -> ProvisionInvitedUserResult | None:
        """
        Resolve an already-linked external identity.
        """

        try:

            link = (
                self._identity_repository
                .get(
                    identity.issuer,
                    identity.subject,
                )
            )

        except KeyError:

            return None

        user = self._user_repository.get(
            link.user_id
        )

        access_grant = None

        if user.is_athlete:

            if user.athlete_id is None:
                raise RuntimeError(
                    "Linked athlete user has no athlete."
                )

            try:

                access_grant = (
                    self._access_repository
                    .get(
                        user.user_id,
                        user.athlete_id,
                    )
                )

            except KeyError as error:

                raise RuntimeError(
                    "Linked athlete user has no "
                    "access grant."
                ) from error

        return ProvisionInvitedUserResult(
            user=user,
            created=False,
            invitation=None,
            access_grant=access_grant,
        )

    def _user_for_invitation(
        self,
        invitation: AlphaInvitation,
    ) -> tuple[User, bool]:
        """
        Reuse a compatible user or create a new one.
        """

        try:

            user = (
                self._user_repository
                .get_by_email(
                    invitation.email
                )
            )

        except KeyError:

            return (
                User(
                    email=invitation.email,
                    role=invitation.role,
                    athlete_id=(
                        invitation.athlete_id
                    ),
                ),
                True,
            )

        if (
            user.role
            != invitation.role
        ):
            raise PermissionError(
                "Existing user role does not "
                "match the invitation."
            )

        if (
            user.athlete_id
            != invitation.athlete_id
        ):
            raise PermissionError(
                "Existing user athlete does not "
                "match the invitation."
            )

        return user, False

    def _validate_existing_access(
        self,
        expected: AthleteAccessGrant,
    ) -> None:
        """
        Ensure an existing grant cannot conflict.
        """

        try:

            existing = (
                self._access_repository
                .get(
                    expected.user_id,
                    expected.athlete_id,
                )
            )

        except KeyError:

            return

        if existing != expected:
            raise PermissionError(
                "Existing athlete access does not "
                "match the invitation."
            )

    def _persist(
        self,
        *,
        user: User,
        created: bool,
        link: ExternalIdentityLink,
        access_grant: AthleteAccessGrant,
        invitation: AlphaInvitation,
        claimed_invitation: AlphaInvitation,
    ) -> None:
        """
        Persist local development records with compensation.
        """

        user_saved = False
        link_saved = False
        grant_saved = False
        invitation_saved = False

        try:

            if created:

                self._user_repository.save(
                    user
                )
                user_saved = True

            self._identity_repository.save(
                link
            )
            link_saved = True

            try:

                self._access_repository.get(
                    access_grant.user_id,
                    access_grant.athlete_id,
                )

            except KeyError:

                self._access_repository.save(
                    access_grant
                )
                grant_saved = True

            self._invitation_repository.save(
                claimed_invitation
            )
            invitation_saved = True

        except Exception as error:

            rollback_errors = []

            if invitation_saved:

                try:
                    self._invitation_repository.save(
                        invitation
                    )
                except Exception as rollback_error:
                    rollback_errors.append(
                        rollback_error
                    )

            if grant_saved:

                try:
                    self._access_repository.delete(
                        access_grant.user_id,
                        access_grant.athlete_id,
                    )
                except Exception as rollback_error:
                    rollback_errors.append(
                        rollback_error
                    )

            if link_saved:

                try:
                    self._identity_repository.delete(
                        link.issuer,
                        link.subject,
                    )
                except Exception as rollback_error:
                    rollback_errors.append(
                        rollback_error
                    )

            if user_saved:

                try:
                    self._user_repository.delete(
                        user.user_id
                    )
                except Exception as rollback_error:
                    rollback_errors.append(
                        rollback_error
                    )

            if rollback_errors:
                raise RuntimeError(
                    "Provisioning failed and local "
                    "rollback was incomplete."
                ) from error

            raise