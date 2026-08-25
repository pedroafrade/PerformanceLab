"""
PerformanceLab

JSON Training Coach consent repository.
"""

import json

from datetime import (
    datetime,
)
from pathlib import (
    Path,
)

from performancelab.training_coach_consent import (
    TrainingCoachConsent,
)


class JsonTrainingCoachConsentRepository:
    """
    Persist versioned Training Coach consent as JSON files.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/training_coach_consents"
        ),
    ) -> None:

        self._directory = Path(
            directory
        )

        self._directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _path_for(
        self,
        consent_id: str,
    ) -> Path:

        if not isinstance(
            consent_id,
            str,
        ):

            raise TypeError(
                "consent_id must be a string."
            )

        normalized_consent_id = (
            consent_id.strip()
        )

        if not normalized_consent_id:

            raise ValueError(
                "consent_id cannot be empty."
            )

        return (
            self._directory
            / f"{normalized_consent_id}.json"
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

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> TrainingCoachConsent:

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
                "Unsupported Training Coach "
                "consent version."
            )

        withdrawn_at = data.get(
            "withdrawn_at"
        )

        return TrainingCoachConsent(
            consent_id=data[
                "consent_id"
            ],
            user_id=data[
                "user_id"
            ],
            policy_version=data[
                "policy_version"
            ],
            granted_at=datetime.fromisoformat(
                data[
                    "granted_at"
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
            for consent in self.list_for_user(
                normalized_user_id
            )
            if (
                consent.policy_version
                == normalized_policy_version
            )
        )

        if not candidates:

            return None

        return max(
            candidates,
            key=lambda consent: (
                consent.granted_at,
                consent.consent_id,
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
                existing.policy_version,
                existing.granted_at,
            )

            supplied_identity = (
                consent.user_id,
                consent.purpose,
                consent.policy_version,
                consent.granted_at,
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
            "policy_version": (
                consent.policy_version
            ),
            "granted_at": (
                consent.granted_at
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
        Delete one Training Coach consent record.
        """

        path = self._path_for(
            consent_id
        )

        if not path.exists():

            raise KeyError(
                "Training Coach consent not found: "
                f"{consent_id}"
            )

        path.unlink()

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
        TrainingCoachConsent,
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
                    consent.granted_at,
                    consent.consent_id,
                ),
            )
        )