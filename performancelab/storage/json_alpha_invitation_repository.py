"""
PerformanceLab

JSON private alpha invitation repository.
"""

import json

from pathlib import (
    Path,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)


class JsonAlphaInvitationRepository:
    """
    Store private alpha invitations as individual JSON files.
    """

    def __init__(
        self,
        directory: str | Path = (
            "data/alpha_invitations"
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
        invitation_id: str,
    ) -> Path:
        """
        Return the path for one invitation.
        """

        if not isinstance(
            invitation_id,
            str,
        ) or not invitation_id.strip():
            raise ValueError(
                "invitation_id cannot be empty."
            )

        return (
            self._directory
            / f"{invitation_id.strip()}.json"
        )

    def get(
        self,
        invitation_id: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by ID.
        """

        path = self._path_for(
            invitation_id
        )

        if not path.exists():

            raise KeyError(
                "Alpha invitation does not exist."
            )

        return self._load_from_path(
            path
        )

    def get_by_email(
        self,
        email: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by normalized email.
        """

        if not isinstance(
            email,
            str,
        ):
            raise TypeError(
                "email must be a string."
            )

        normalized_email = (
            email
            .strip()
            .lower()
        )

        for invitation in self.list():

            if (
                invitation.email
                == normalized_email
            ):
                return invitation

        raise KeyError(
            "Alpha invitation does not exist."
        )

    def save(
        self,
        invitation: AlphaInvitation,
    ) -> None:
        """
        Save an invitation while preserving email uniqueness.
        """

        if not isinstance(
            invitation,
            AlphaInvitation,
        ):
            raise TypeError(
                "invitation must be an AlphaInvitation."
            )

        for existing in self.list():

            if (
                existing.email
                == invitation.email
                and existing.invitation_id
                != invitation.invitation_id
            ):
                raise ValueError(
                    "An invitation already exists "
                    "for this email."
                )

        path = self._path_for(
            invitation.invitation_id
        )

        data = {
            "version": 1,
            "invitation_id": (
                invitation.invitation_id
            ),
            "email": invitation.email,
            "role": invitation.role,
            "athlete_id": (
                invitation.athlete_id
            ),
            "claimed_by_user_id": (
                invitation
                .claimed_by_user_id
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

    def list(
        self,
    ) -> list[
        AlphaInvitation
    ]:
        """
        Return every invitation ordered by email.
        """

        invitations = [
            self._load_from_path(
                path
            )
            for path
            in self._directory.glob(
                "*.json"
            )
        ]

        return sorted(
            invitations,
            key=lambda invitation: (
                invitation.email
            ),
        )

    def delete(
        self,
        invitation_id: str,
    ) -> None:
        """
        Delete an invitation.
        """

        path = self._path_for(
            invitation_id
        )

        if not path.exists():

            raise KeyError(
                "Alpha invitation does not exist."
            )

        path.unlink()

    @staticmethod
    def _load_from_path(
        path: Path,
    ) -> AlphaInvitation:
        """
        Load and validate one persisted invitation.
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
                "Unsupported alpha invitation version."
            )

        return AlphaInvitation(
            invitation_id=(
                data["invitation_id"]
            ),
            email=data["email"],
            role=data["role"],
            athlete_id=(
                data.get(
                    "athlete_id"
                )
            ),
            claimed_by_user_id=(
                data.get(
                    "claimed_by_user_id"
                )
            ),
        )