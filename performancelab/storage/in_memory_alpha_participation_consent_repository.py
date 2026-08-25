"""
PerformanceLab

In-memory private alpha consent repository.
"""

from performancelab.alpha_participation_consent import (
    AlphaParticipationConsent,
)


class InMemoryAlphaParticipationConsentRepository:
    """
    Deterministic repository for application tests.
    """

    def __init__(
        self,
        consents=(),
    ) -> None:

        self._consents: dict[
            str,
            AlphaParticipationConsent,
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

        candidates = tuple(
            consent
            for consent
            in self._consents.values()
            if (
                consent.user_id
                == normalized_user_id
                and consent.notice_version
                == normalized_notice_version
            )
        )

        if not candidates:

            return None

        return max(
            candidates,
            key=lambda consent: (
                consent.accepted_at,
                consent.consent_id,
            ),
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

        existing = self._consents.get(
            consent.consent_id
        )

        if existing is not None:

            existing_identity = (
                existing.user_id,
                existing.purpose,
                existing.notice_version,
                existing.accepted_at,
            )

            supplied_identity = (
                consent.user_id,
                consent.purpose,
                consent.notice_version,
                consent.accepted_at,
            )

            if (
                existing_identity
                != supplied_identity
            ):

                raise ValueError(
                    "Consent identity cannot be "
                    "changed after it is saved."
                )

        self._consents[
            consent.consent_id
        ] = consent

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
                    consent.accepted_at,
                    consent.consent_id,
                ),
            )
        )