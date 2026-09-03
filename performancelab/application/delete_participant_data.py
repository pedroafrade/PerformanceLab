"""
PerformanceLab

Delete all active data associated with one alpha participant.
"""

from dataclasses import (
    dataclass,
)

from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.identity import (
    User,
)


@dataclass(
    frozen=True
)
class DeleteParticipantDataResult:
    """
    Identifiers of the deleted participant resources.
    """

    user_id: str
    athlete_id: str


class DeleteParticipantData:
    """
    Delete an athlete participant and associated active data.
    """

    def __init__(
        self,
        *,
        athlete_repository,
        user_repository,
        external_identity_repository,
        invitation_repository,
        athlete_access_repository,
        alpha_participation_consent_repository,
        training_coach_consent_repository,
        training_coach_usage_repository,
        authorization: AthleteAuthorizationService,
        transaction_factory,
        daily_brief_privacy_repository=None,
    ) -> None:

        if not isinstance(
            authorization,
            AthleteAuthorizationService,
        ):

            raise TypeError(
                "authorization must be an "
                "AthleteAuthorizationService."
            )

        if not callable(
            transaction_factory
        ):

            raise TypeError(
                "transaction_factory must be callable."
            )

        self._athlete_repository = (
            athlete_repository
        )
        self._user_repository = (
            user_repository
        )
        self._external_identity_repository = (
            external_identity_repository
        )
        self._invitation_repository = (
            invitation_repository
        )
        self._athlete_access_repository = (
            athlete_access_repository
        )
        self._alpha_consent_repository = (
            alpha_participation_consent_repository
        )
        self._training_coach_consent_repository = (
            training_coach_consent_repository
        )
        self._training_coach_usage_repository = (
            training_coach_usage_repository
        )
        self._authorization = authorization
        self._daily_brief_privacy_repository = daily_brief_privacy_repository
        self._transaction_factory = (
            transaction_factory
        )

    def execute(
        self,
        user: User,
    ) -> DeleteParticipantDataResult:
        """
        Delete one authenticated athlete owner's active data.
        """

        if not isinstance(
            user,
            User,
        ):

            raise TypeError(
                "user must be a User."
            )

        if not user.is_athlete:

            raise PermissionError(
                "Only athlete accounts can delete "
                "private alpha participant data."
            )

        if user.athlete_id is None:

            raise ValueError(
                "Athlete user has no athlete profile."
            )

        user_id = user.user_id
        athlete_id = user.athlete_id

        self._authorization.require_access(
            user_id=user_id,
            athlete_id=athlete_id,
            allowed_permissions=(
                "owner",
            ),
        )

        identity_links = tuple(
            link
            for link
            in (
                self
                ._external_identity_repository
                .list()
            )
            if (
                link.user_id
                == user_id
            )
        )

        invitations = tuple(
            invitation
            for invitation
            in (
                self
                ._invitation_repository
                .list()
            )
            if (
                invitation.email
                == user.email
                or (
                    invitation
                    .claimed_by_user_id
                    == user_id
                )
                or (
                    invitation.athlete_id
                    == athlete_id
                )
            )
        )

        access_grants = tuple(
            self
            ._athlete_access_repository
            .list_for_athlete(
                athlete_id
            )
        )

        alpha_consents = tuple(
            self
            ._alpha_consent_repository
            .list_for_user(
                user_id
            )
        )

        training_coach_consents = tuple(
            self
            ._training_coach_consent_repository
            .list_for_user(
                user_id
            )
        )

        usage_events = tuple(
            self
            ._training_coach_usage_repository
            .list_for_user(
                user_id
            )
        )

        with self._transaction_factory():

            # Same transaction as the owner/account deletion. Never use the
            # generation store's separate Engine transaction here.
            if self._daily_brief_privacy_repository is not None:
                self._daily_brief_privacy_repository.delete_for_user(user_id)

            for link in identity_links:

                self._external_identity_repository.delete(
                    link.issuer,
                    link.subject,
                )

            for invitation in invitations:

                self._invitation_repository.delete(
                    invitation.invitation_id
                )

            for grant in access_grants:

                self._athlete_access_repository.delete(
                    grant.user_id,
                    grant.athlete_id,
                )

            for consent in alpha_consents:

                self._alpha_consent_repository.delete(
                    consent.consent_id
                )

            for consent in training_coach_consents:

                self._training_coach_consent_repository.delete(
                    consent.consent_id
                )

            for event in usage_events:

                self._training_coach_usage_repository.delete(
                    event.usage_id
                )

            self._user_repository.delete(
                user_id
            )

            self._athlete_repository.delete(
                athlete_id
            )

        return DeleteParticipantDataResult(
            user_id=user_id,
            athlete_id=athlete_id,
        )
