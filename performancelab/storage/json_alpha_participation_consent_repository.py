"""
PerformanceLab

JSON private alpha participation consent repository.
"""

import json

from datetime import (
    datetime,
)
from pathlib import (
    Path,
)

from performancelab.alpha_participation_consent import (
    AlphaParticipationConsent,
)


class JsonAlphaParticipationConsentRepository:
    """
    Persist private alpha consent as JSON files.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/alpha_participation_consents"
        ),
    ) -> None:

        self._directory = Path(
            directory
        )

        self._directory.mkdir(
            parents=True,
            exist_ok=True,
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

    def _path_for(
        self,
        consent_id: str,
    ) -> Path:

        normalized_consent_id = (
            self._normalized_text(
                consent_id,
                field_name="consent_id",
            )
        )

        if (
            Path(
                normalized_consent_id
            ).name
            != normalized_consent_id
            or "/"
            in normalized_consent_id
            or "\\"
            in normalized_consent_id
        ):

            raise ValueError(
                "consent_id cannot contain "
                "a file path."
            )

        return (
            self._directory
            / f"{normalized_consent_id}.json"
        )

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> AlphaParticipationConsent:

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(
                file
            )

        if data.get(
            "version"
        ) != 1:

            raise ValueError(
                "Unsupported private alpha "
                "consent version."
            )

        withdrawn_at = data.get(
            "withdrawn_at"
        )

        return AlphaParticipationConsent(
            consent_id=data[
                "consent_id"
            ],
            user_id=data[
                "user_id"
            ],
            notice_version=data[
                "notice_version"
            ],
            accepted_at=datetime.fromisoformat(
                data[
                    "accepted_at"
                ]
            ),
            withdrawn_at=(
                datetime.fromisoformat(
                    withdrawn_at
                )
                if withdrawn_at
                is not None
                else None
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

        candidates = tuple(
            consent
            for consent in self.list_for_user(
                normalized_user_id
            )
            if (
                consent.notice_version
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

        path = self._path_for(
            consent.consent_id
        )

        if path.exists():

            existing = (
                self._load_from_path(
                    path
                )
            )

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

        data = {
            "version": 1,
            "consent_id": (
                consent.consent_id
            ),
            "user_id": consent.user_id,
            "purpose": consent.purpose,
            "notice_version": (
                consent.notice_version
            ),
            "accepted_at": (
                consent.accepted_at
                .isoformat()
            ),
            "withdrawn_at": (
                consent.withdrawn_at
                .isoformat()
                if (
                    consent.withdrawn_at
                    is not None
                )
                else None
            ),
        }

        temporary_path = (
            path.with_suffix(
                ".tmp"
            )
        )

        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_path.replace(
            path
        )

    def delete(
        self,
        consent_id: str,
    ) -> None:
        """
        Delete one private alpha consent record.
        """

        path = self._path_for(
            consent_id
        )

        if not path.exists():

            raise KeyError(
                "Private alpha consent not found: "
                f"{consent_id}"
            )

        path.unlink()

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
            consent
            for consent in self.list()
            if (
                consent.user_id
                == normalized_user_id
            )
        )

    def list(
        self,
    ) -> tuple[
        AlphaParticipationConsent,
        ...,
    ]:

        consents = tuple(
            self._load_from_path(
                path
            )
            for path
            in self._directory.glob(
                "*.json"
            )
        )

        return tuple(
            sorted(
                consents,
                key=lambda consent: (
                    consent.accepted_at,
                    consent.consent_id,
                ),
            )
        )