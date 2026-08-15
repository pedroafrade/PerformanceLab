"""
PerformanceLab

JSON external identity repository.
"""

import hashlib
import json

from pathlib import (
    Path,
)

from performancelab.identity import (
    ExternalIdentityLink,
)


class JsonExternalIdentityRepository:
    """
    Store external identity links in individual JSON files.

    This local implementation supports development while
    preserving the contract that will later be implemented
    transactionally in PostgreSQL.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/external_identities"
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
    def _normalized_key(
        issuer: str,
        subject: str,
    ) -> tuple[str, str]:
        """
        Normalize and validate a provider identity key.
        """

        if not isinstance(
            issuer,
            str,
        ):
            raise TypeError(
                "issuer must be a string."
            )

        if not isinstance(
            subject,
            str,
        ):
            raise TypeError(
                "subject must be a string."
            )

        normalized_issuer = (
            issuer.strip()
        )
        normalized_subject = (
            subject.strip()
        )

        if not normalized_issuer:
            raise ValueError(
                "issuer cannot be empty."
            )

        if not normalized_subject:
            raise ValueError(
                "subject cannot be empty."
            )

        return (
            normalized_issuer,
            normalized_subject,
        )

    def _path_for(
        self,
        issuer: str,
        subject: str,
    ) -> Path:
        """
        Return a filesystem-safe path for the identity.
        """

        provider_key = (
            self._normalized_key(
                issuer,
                subject,
            )
        )

        serialized_key = json.dumps(
            provider_key,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )

        digest = hashlib.sha256(
            serialized_key.encode(
                "utf-8"
            )
        ).hexdigest()

        return (
            self._directory
            / f"{digest}.json"
        )

    def get(
        self,
        issuer: str,
        subject: str,
    ) -> ExternalIdentityLink:
        """
        Return one external identity link.
        """

        path = self._path_for(
            issuer,
            subject,
        )

        if not path.exists():

            raise KeyError(
                "External identity link "
                "does not exist."
            )

        return self._load_from_path(
            path
        )

    def save(
        self,
        link: ExternalIdentityLink,
    ) -> None:
        """
        Persist a link without allowing reassignment.
        """

        if not isinstance(
            link,
            ExternalIdentityLink,
        ):
            raise TypeError(
                "link must be an "
                "ExternalIdentityLink."
            )

        path = self._path_for(
            link.issuer,
            link.subject,
        )

        if path.exists():

            existing = (
                self._load_from_path(
                    path
                )
            )

            if (
                existing.user_id
                != link.user_id
            ):
                raise ValueError(
                    "External identity is already "
                    "linked to another user."
                )

            return

        data = {
            "version": 1,
            "issuer": link.issuer,
            "subject": link.subject,
            "user_id": link.user_id,
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
        issuer: str,
        subject: str,
    ) -> None:
        """
        Delete one external identity link.
        """

        path = self._path_for(
            issuer,
            subject,
        )

        if not path.exists():

            raise KeyError(
                "External identity link "
                "does not exist."
            )

        path.unlink()

    def list(
        self,
    ) -> list[
        ExternalIdentityLink
    ]:
        """
        Return all stored external identity links.
        """

        links = [
            self._load_from_path(
                path
            )
            for path
            in self._directory.glob(
                "*.json"
            )
        ]

        return sorted(
            links,
            key=lambda link: (
                link.issuer,
                link.subject,
            ),
        )

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> ExternalIdentityLink:
        """
        Load and validate one persisted link.
        """

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
                "Unsupported external identity "
                "link version."
            )

        return ExternalIdentityLink(
            issuer=data["issuer"],
            subject=data["subject"],
            user_id=data["user_id"],
        )