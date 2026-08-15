"""
PerformanceLab

PostgreSQL external identity repository.
"""

from sqlalchemy import (
    delete,
    insert,
    select,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.identity import (
    ExternalIdentityLink,
)
from performancelab.storage.postgresql_schema import (
    external_identities,
)


class PostgreSQLExternalIdentityRepository:
    """
    Store external identity links in PostgreSQL.

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
    def _link_from_row(
        row,
    ) -> ExternalIdentityLink:
        """
        Convert one database row into an identity link.
        """

        return ExternalIdentityLink(
            issuer=row["issuer"],
            subject=row["subject"],
            user_id=row["user_id"],
        )

    @staticmethod
    def _normalized_key(
        issuer: str,
        subject: str,
    ) -> tuple[
        str,
        str,
    ]:
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

    def get(
        self,
        issuer: str,
        subject: str,
    ) -> ExternalIdentityLink:
        """
        Return one external identity link.
        """

        (
            normalized_issuer,
            normalized_subject,
        ) = self._normalized_key(
            issuer,
            subject,
        )

        row = self._connection.execute(
            select(
                external_identities
            ).where(
                external_identities.c.issuer
                == normalized_issuer,
                external_identities.c.subject
                == normalized_subject,
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                "External identity link does not exist."
            )

        return self._link_from_row(
            row
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
                "link must be an ExternalIdentityLink."
            )

        row = self._connection.execute(
            select(
                external_identities.c.user_id
            ).where(
                external_identities.c.issuer
                == link.issuer,
                external_identities.c.subject
                == link.subject,
            )
        ).mappings().one_or_none()

        if row is not None:

            if (
                row["user_id"]
                != link.user_id
            ):
                raise ValueError(
                    "External identity is already "
                    "linked to another user."
                )

            return

        self._connection.execute(
            insert(
                external_identities
            ).values(
                issuer=link.issuer,
                subject=link.subject,
                user_id=link.user_id,
            )
        )

    def delete(
        self,
        issuer: str,
        subject: str,
    ) -> None:
        """
        Delete one external identity link.
        """

        (
            normalized_issuer,
            normalized_subject,
        ) = self._normalized_key(
            issuer,
            subject,
        )

        result = self._connection.execute(
            delete(
                external_identities
            ).where(
                external_identities.c.issuer
                == normalized_issuer,
                external_identities.c.subject
                == normalized_subject,
            )
        )

        if result.rowcount == 0:
            raise KeyError(
                "External identity link does not exist."
            )

    def list(
        self,
    ) -> list[
        ExternalIdentityLink
    ]:
        """
        Return every stored identity link.
        """

        rows = self._connection.execute(
            select(
                external_identities
            ).order_by(
                external_identities.c.issuer,
                external_identities.c.subject,
            )
        ).mappings().all()

        return [
            self._link_from_row(
                row
            )
            for row in rows
        ]