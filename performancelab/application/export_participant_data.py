"""
PerformanceLab

Export all private alpha data associated with one participant.
"""

import json

from dataclasses import (
    dataclass,
)
from datetime import (
    datetime,
)

from performancelab.authorization import (
    AthleteAuthorizationService,
)
from performancelab.identity import (
    User,
)
from performancelab.storage.json import (
    athlete_to_dict,
)


EXPORT_FORMAT = (
    "PerformanceLab participant data export"
)

EXPORT_VERSION = 1


def _timestamp(
    value: datetime | None,
) -> str | None:
    """
    Serialize an optional timezone-aware timestamp.
    """

    if value is None:

        return None

    return value.isoformat()


@dataclass(
    frozen=True
)
class ExportParticipantDataResult:
    """
    Complete serializable participant export.
    """

    data: dict

    def to_json(
        self,
    ) -> str:
        """
        Return readable UTF-8 JSON.
        """

        return json.dumps(
            self.data,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
        )


class ExportParticipantData:
    """
    Export data only for an authenticated athlete owner.
    """

    def __init__(
        self,
        *,
        athlete_repository,
        external_identity_repository,
        athlete_access_repository,
        alpha_participation_consent_repository,
        training_coach_consent_repository,
        training_coach_usage_repository,
        authorization: AthleteAuthorizationService,
    ) -> None:

        if not isinstance(
            authorization,
            AthleteAuthorizationService,
        ):

            raise TypeError(
                "authorization must be an "
                "AthleteAuthorizationService."
            )

        self._athlete_repository = (
            athlete_repository
        )
        self._external_identity_repository = (
            external_identity_repository
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

    def execute(
        self,
        user: User,
        *,
        generated_at: datetime,
    ) -> ExportParticipantDataResult:
        """
        Build the complete export for one athlete participant.
        """

        if not isinstance(
            user,
            User,
        ):

            raise TypeError(
                "user must be a User."
            )

        if not isinstance(
            generated_at,
            datetime,
        ):

            raise TypeError(
                "generated_at must be a datetime."
            )

        if (
            generated_at.tzinfo is None
            or generated_at.utcoffset() is None
        ):

            raise ValueError(
                "generated_at must include a timezone."
            )

        if not user.is_athlete:

            raise PermissionError(
                "Only athlete accounts can export "
                "private alpha participant data."
            )

        if user.athlete_id is None:

            raise ValueError(
                "Athlete user has no athlete profile."
            )

        self._authorization.require_access(
            user_id=user.user_id,
            athlete_id=user.athlete_id,
            allowed_permissions=(
                "owner",
            ),
        )

        athlete = (
            self._athlete_repository.get(
                user.athlete_id
            )
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
                == user.user_id
            )
        )

        access_grants = tuple(
            grant
            for grant
            in (
                self
                ._athlete_access_repository
                .list_for_user(
                    user.user_id
                )
            )
            if (
                grant.athlete_id
                == user.athlete_id
            )
        )

        alpha_consents = (
            self
            ._alpha_consent_repository
            .list_for_user(
                user.user_id
            )
        )

        training_coach_consents = (
            self
            ._training_coach_consent_repository
            .list_for_user(
                user.user_id
            )
        )

        usage_events = (
            self
            ._training_coach_usage_repository
            .list_for_user(
                user.user_id
            )
        )

        data = {
            "format": EXPORT_FORMAT,
            "version": EXPORT_VERSION,
            "generated_at": (
                generated_at.isoformat()
            ),
            "participant": {
                "user_id": user.user_id,
                "email": user.email,
                "role": user.role,
                "athlete_id": (
                    user.athlete_id
                ),
            },
            "external_identities": [
                {
                    "issuer": link.issuer,
                    "subject": link.subject,
                    "user_id": link.user_id,
                }
                for link in identity_links
            ],
            "athlete_access": [
                {
                    "user_id": grant.user_id,
                    "athlete_id": (
                        grant.athlete_id
                    ),
                    "permission": (
                        grant.permission
                    ),
                }
                for grant in access_grants
            ],
            "alpha_participation_consents": [
                {
                    "consent_id": (
                        consent.consent_id
                    ),
                    "user_id": (
                        consent.user_id
                    ),
                    "purpose": (
                        consent.purpose
                    ),
                    "notice_version": (
                        consent.notice_version
                    ),
                    "accepted_at": (
                        consent.accepted_at
                        .isoformat()
                    ),
                    "withdrawn_at": (
                        _timestamp(
                            consent.withdrawn_at
                        )
                    ),
                }
                for consent in alpha_consents
            ],
            "training_coach_consents": [
                {
                    "consent_id": (
                        consent.consent_id
                    ),
                    "user_id": (
                        consent.user_id
                    ),
                    "purpose": (
                        consent.purpose
                    ),
                    "policy_version": (
                        consent.policy_version
                    ),
                    "granted_at": (
                        consent.granted_at
                        .isoformat()
                    ),
                    "withdrawn_at": (
                        _timestamp(
                            consent.withdrawn_at
                        )
                    ),
                }
                for consent
                in training_coach_consents
            ],
            "training_coach_usage": [
                {
                    "usage_id": event.usage_id,
                    "user_id": event.user_id,
                    "occurred_at": (
                        event.occurred_at
                        .isoformat()
                    ),
                    "status": (
                        event.status.value
                    ),
                    "provider": event.provider,
                    "model": event.model,
                    "error_code": (
                        event.error_code
                    ),
                    "latency_ms": (
                        event.latency_ms
                    ),
                    "remaining_user_requests": (
                        event
                        .remaining_user_requests
                    ),
                    "remaining_global_requests": (
                        event
                        .remaining_global_requests
                    ),
                }
                for event in usage_events
            ],
            "athlete": athlete_to_dict(
                athlete
            ),
        }

        return ExportParticipantDataResult(
            data=data
        )