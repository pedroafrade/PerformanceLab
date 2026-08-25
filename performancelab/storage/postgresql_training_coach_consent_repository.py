"""
PerformanceLab

PostgreSQL Training Coach consent repository.
"""

from datetime import (
    timezone,
)

from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.storage.postgresql_schema import (
    training_coach_consents,
)
from performancelab.training_coach_consent import (
    TrainingCoachConsent,
)


class PostgreSQLTrainingCoachConsentRepository:
    """
    Persist versioned consent using a shared SQLAlchemy connection.
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
                "connection must be a SQLAlchemy Connection."
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
    ) -> TrainingCoachConsent:

        return TrainingCoachConsent(
            consent_id=row[
                "consent_id"
            ],
            user_id=row[
                "user_id"
            ],
            policy_version=row[
                "policy_version"
            ],
            granted_at=(
                cls._aware_datetime(
                    row[
                        "granted_at"
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
        policy_version: str,
    ) -> TrainingCoachConsent | None:

        normalized_user_id = (
            self._normalized_text(
                user_id,
                field_name="user_id",
            )
        )

        normalized_policy_version = (
            self._normalized_text(
                policy_version,
                field_name=(
                    "policy_version"
                ),
            )
        )

        row = self._connection.execute(
            select(
                training_coach_consents
            )
            .where(
                training_coach_consents
                .c
                .user_id
                == normalized_user_id
            )
            .where(
                training_coach_consents
                .c
                .policy_version
                == normalized_policy_version
            )
            .order_by(
                training_coach_consents
                .c
                .granted_at
                .desc(),
                training_coach_consents
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
        consent: TrainingCoachConsent,
    ) -> None:

        if not isinstance(
            consent,
            TrainingCoachConsent,
        ):

            raise TypeError(
                "consent must be a "
                "TrainingCoachConsent."
            )

        existing = self._connection.execute(
            select(
                training_coach_consents
            ).where(
                training_coach_consents
                .c
                .consent_id
                == consent.consent_id
            )
        ).mappings().one_or_none()

        if existing is None:

            self._connection.execute(
                insert(
                    training_coach_consents
                ).values(
                    consent_id=(
                        consent.consent_id
                    ),
                    user_id=(
                        consent.user_id
                    ),
                    purpose=(
                        consent.purpose
                    ),
                    policy_version=(
                        consent.policy_version
                    ),
                    granted_at=(
                        consent.granted_at
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
                "purpose"
            ],
            existing[
                "policy_version"
            ],
            self._aware_datetime(
                existing[
                    "granted_at"
                ]
            ),
        )

        supplied_identity = (
            consent.user_id,
            consent.purpose,
            consent.policy_version,
            consent.granted_at,
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
                training_coach_consents
            )
            .where(
                training_coach_consents
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

    def delete(
        self,
        consent_id: str,
    ) -> None:
        """
        Delete one Training Coach consent record.
        """

        normalized_consent_id = (
            self._normalized_text(
                consent_id,
                field_name="consent_id",
            )
        )

        result = self._connection.execute(
            delete(
                training_coach_consents
            ).where(
                training_coach_consents
                .c
                .consent_id
                == normalized_consent_id
            )
        )

        if result.rowcount != 1:

            raise KeyError(
                "Training Coach consent not found: "
                f"{normalized_consent_id}"
            )

    def list_for_user(
        self,
        user_id: str,
    ) -> tuple[
        TrainingCoachConsent,
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
                training_coach_consents
            )
            .where(
                training_coach_consents
                .c
                .user_id
                == normalized_user_id
            )
            .order_by(
                training_coach_consents
                .c
                .granted_at,
                training_coach_consents
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