"""
PerformanceLab

PostgreSQL private alpha invitation repository.
"""

from sqlalchemy import (
    delete,
    insert,
    select,
    update,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.storage.postgresql_schema import (
    alpha_invitations,
)


class PostgreSQLAlphaInvitationRepository:
    """
    Store private alpha invitations in PostgreSQL.

    The supplied connection controls the transaction.
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
    def _invitation_from_row(
        row,
    ) -> AlphaInvitation:
        """
        Convert a database row into an invitation.
        """

        return AlphaInvitation(
            invitation_id=(
                row["invitation_id"]
            ),
            email=row["email"],
            role=row["role"],
            athlete_id=row["athlete_id"],
            claimed_by_user_id=(
                row["claimed_by_user_id"]
            ),
        )

    @staticmethod
    def _normalized_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        """
        Normalize and validate a text lookup value.
        """

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

    def get(
        self,
        invitation_id: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by ID.
        """

        normalized_invitation_id = (
            self._normalized_text(
                invitation_id,
                field_name="invitation_id",
            )
        )

        row = self._connection.execute(
            select(
                alpha_invitations
            ).where(
                alpha_invitations
                .c
                .invitation_id
                == normalized_invitation_id
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                "Alpha invitation does not exist."
            )

        return self._invitation_from_row(
            row
        )

    def get_by_email(
        self,
        email: str,
    ) -> AlphaInvitation:
        """
        Return an invitation by normalized email.
        """

        normalized_email = (
            self._normalized_text(
                email,
                field_name="email",
            ).lower()
        )

        row = self._connection.execute(
            select(
                alpha_invitations
            ).where(
                alpha_invitations.c.email
                == normalized_email
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                "Alpha invitation does not exist."
            )

        return self._invitation_from_row(
            row
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

        invitation_with_email = (
            self._connection.execute(
                select(
                    alpha_invitations
                    .c
                    .invitation_id
                ).where(
                    alpha_invitations.c.email
                    == invitation.email
                )
            ).first()
        )

        if (
            invitation_with_email is not None
            and invitation_with_email[0]
            != invitation.invitation_id
        ):
            raise ValueError(
                "An invitation already exists "
                "for this email."
            )

        existing = self._connection.execute(
            select(
                alpha_invitations
                .c
                .invitation_id
            ).where(
                alpha_invitations
                .c
                .invitation_id
                == invitation.invitation_id
            )
        ).first()

        values = {
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

        if existing is None:

            self._connection.execute(
                insert(
                    alpha_invitations
                ).values(
                    invitation_id=(
                        invitation
                        .invitation_id
                    ),
                    **values,
                )
            )

            return

        self._connection.execute(
            update(
                alpha_invitations
            ).where(
                alpha_invitations
                .c
                .invitation_id
                == invitation.invitation_id
            ).values(
                **values
            )
        )

    def list(
        self,
    ) -> list[
        AlphaInvitation
    ]:
        """
        Return all invitations ordered by email.
        """

        rows = self._connection.execute(
            select(
                alpha_invitations
            ).order_by(
                alpha_invitations.c.email
            )
        ).mappings().all()

        return [
            self._invitation_from_row(
                row
            )
            for row in rows
        ]

    def delete(
        self,
        invitation_id: str,
    ) -> None:
        """
        Delete an invitation.
        """

        normalized_invitation_id = (
            self._normalized_text(
                invitation_id,
                field_name="invitation_id",
            )
        )

        result = self._connection.execute(
            delete(
                alpha_invitations
            ).where(
                alpha_invitations
                .c
                .invitation_id
                == normalized_invitation_id
            )
        )

        if result.rowcount == 0:
            raise KeyError(
                "Alpha invitation does not exist."
            )