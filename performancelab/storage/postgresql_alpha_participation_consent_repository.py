"""
PerformanceLab

PostgreSQL private alpha participation consent repository.
"""

from datetime import (
    timezone,
)

from sqlalchemy import (
    insert,
    select,
    update,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.alpha_participation_consent import (
    AlphaParticipationConsent,
)
from performancelab.storage.postgresql_schema import (
    alpha_participation_consents,
)


class PostgreSQLAlphaParticipationConsentRepository:
    """
    Persist versioned private alpha consent.
    """

    def __init__(
        self,
        connection: Connection,
    ) -> None:

        if not isinstance(
            connection,
            Connection,
        ):

            raise TypeError(
                "connection must be a "
                "SQLAlchemy Connection."
            )

        self._connection = connection

    @staticmethod
    def _normalized_text(
        value,
        *,
        field_name: str,
    ) -> str:

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

        return normalized_value

    @staticmethod
    def _aware_datetime(
        value,
    ):

        if (
            value is not None
            and value.tzinfo is None
        ):

            return value.replace(
                tzinfo=timezone.utc
            )

        return value

    @classmethod
    def _consent_from_row(
        cls,
        row,
    ) -> AlphaParticipationConsent:

        return AlphaParticipationConsent(
            consent_id=row[
                "consent_id"
            ],
            user_id=row[
                "user_id"
            ],
            notice_version=row[
                "notice_version"
            ],
            accepted_at=(
                cls._aware_datetime(
                    row[
                        "accepted_at"
                    ]
                )
            ),
            withdrawn_at=(
                cls._aware_datetime(
                    row[
                        "withdrawn_at"
                    ]
                )
            ),
        )

    def latest(
        self,
        *,
        user_id: str,
        notice_version: str,
    ) -> AlphaParticipationConsent | None:

        normalized_user_id = (
            self._normalized_text(
                user_id,
                field_name="user_id",
            )
        )

        normalized_notice_version = (
            self._normalized_text(
                notice_version,
                field_name="notice_version",
            )
        )

        row = self._connection.execute(
            select(
                alpha_participation_consents
            )
            .where(
                alpha_participation_consents
                .c
                .user_id
                == normalized_user_id
            )
            .where(
                alpha_participation_consents
                .c
                .notice_version
                == normalized_notice_version
            )
            .order_by(
                alpha_participation_consents
                .c
                .accepted_at
                .desc(),
                alpha_participation_consents
                .c
                .consent_id
                .desc(),
            )
            .limit(
                1
            )
        ).mappings().one_or_none()

        if row is None:

            return None

        return self._consent_from_row(
            row
        )

    def save(
        self,
        consent: AlphaParticipationConsent,
    ) -> None:

        if not isinstance(
            consent,
            AlphaParticipationConsent,
        ):

            raise TypeError(
                "consent must be an "
                "AlphaParticipationConsent."
            )

        existing = self._connection.execute(
            select(
                alpha_participation_consents
            ).where(
                alpha_participation_consents
                .c
                .consent_id
                == consent.consent_id
            )
        ).mappings().one_or_none()

        if existing is None:

            self._connection.execute(
                insert(
                    alpha_participation_consents
                ).values(
                    consent_id=(
                        consent.consent_id
                    ),
                    user_id=(
                        consent.user_id
                    ),
                    notice_version=(
                        consent.notice_version
                    ),
                    accepted_at=(
                        consent.accepted_at
                    ),
                    withdrawn_at=(
                        consent.withdrawn_at
                    ),
                )
            )

            return

        immutable_identity = (
            existing[
                "user_id"
            ],
            existing[
                "notice_version"
            ],
            self._aware_datetime(
                existing[
                    "accepted_at"
                ]
            ),
        )

        supplied_identity = (
            consent.user_id,
            consent.notice_version,
            consent.accepted_at,
        )

        if (
            immutable_identity
            != supplied_identity
        ):

            raise ValueError(
                "Consent identity cannot be "
                "changed after it is saved."
            )

        self._connection.execute(
            update(
                alpha_participation_consents
            )
            .where(
                alpha_participation_consents
                .c
                .consent_id
                == consent.consent_id
            )
            .values(
                withdrawn_at=(
                    consent.withdrawn_at
                )
            )
        )

    def list_for_user(
        self,
        user_id: str,
    ) -> tuple[
        AlphaParticipationConsent,
        ...,
    ]:

        normalized_user_id = (
            self._normalized_text(
                user_id,
                field_name="user_id",
            )
        )

        rows = self._connection.execute(
            select(
                alpha_participation_consents
            )
            .where(
                alpha_participation_consents
                .c
                .user_id
                == normalized_user_id
            )
            .order_by(
                alpha_participation_consents
                .c
                .accepted_at,
                alpha_participation_consents
                .c
                .consent_id,
            )
        ).mappings().all()

        return tuple(
            self._consent_from_row(
                row
            )
            for row in rows
        )