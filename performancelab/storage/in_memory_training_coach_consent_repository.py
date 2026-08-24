"""
PerformanceLab

In-memory Training Coach consent repository.
"""

from performancelab.training_coach_consent import (
    TrainingCoachConsent,
)


class InMemoryTrainingCoachConsentRepository:
    """
    Deterministic consent repository for application tests.
    """

    def __init__(
        self,
        consents=(),
    ) -> None:

        self._consents: dict[
            str,
            TrainingCoachConsent,
        ] = {}

        for consent in consents:

            self.save(
                consent
            )

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

        candidates = tuple(
            consent
            for consent
            in self._consents.values()
            if (
                consent.user_id
                == normalized_user_id
                and consent.policy_version
                == normalized_policy_version
            )
        )

        if not candidates:

            return None

        return max(
            candidates,
            key=lambda consent: (
                consent.granted_at
            ),
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

        self._consents[
            consent.consent_id
        ] = consent

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

        return tuple(
            sorted(
                (
                    consent
                    for consent
                    in self._consents.values()
                    if (
                        consent.user_id
                        == normalized_user_id
                    )
                ),
                key=lambda consent: (
                    consent.granted_at
                ),
            )
        )