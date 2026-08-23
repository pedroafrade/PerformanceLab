"""
PerformanceLab

PostgreSQL athlete access repository.
"""

from sqlalchemy import (
    delete,
    insert,
    select,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.storage.postgresql_schema import (
    user_athlete_access,
)


class PostgreSQLAthleteAccessRepository:
    """
    Store athlete access grants in PostgreSQL.

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
    def _grant_from_row(
        row,
    ) -> AthleteAccessGrant:
        """
        Convert a database row into an access grant.
        """

        return AthleteAccessGrant(
            user_id=row["user_id"],
            athlete_id=row["athlete_id"],
            permission=row["permission"],
        )

    @staticmethod
    def _normalized_key(
        user_id: str,
        athlete_id: str,
    ) -> tuple[
        str,
        str,
    ]:
        """
        Normalize and validate an access grant key.
        """

        normalized_values = []

        for field_name, value in (
            (
                "user_id",
                user_id,
            ),
            (
                "athlete_id",
                athlete_id,
            ),
        ):

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

            normalized_values.append(
                normalized_value
            )

        return (
            normalized_values[0],
            normalized_values[1],
        )

    @staticmethod
    def _normalized_value(
        value: str,
        *,
        field_name: str,
    ) -> str:
        """
        Normalize one user or athlete identifier.
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
        user_id: str,
        athlete_id: str,
    ) -> AthleteAccessGrant:
        """
        Return one explicit access grant.
        """

        (
            normalized_user_id,
            normalized_athlete_id,
        ) = self._normalized_key(
            user_id,
            athlete_id,
        )

        row = self._connection.execute(
            select(
                user_athlete_access
            ).where(
                user_athlete_access.c.user_id
                == normalized_user_id,
                user_athlete_access.c.athlete_id
                == normalized_athlete_id,
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                "Athlete access grant does not exist."
            )

        return self._grant_from_row(
            row
        )

    def save(
        self,
        grant: AthleteAccessGrant,
    ) -> None:
        """
        Save a grant without silently changing permission.
        """

        if not isinstance(
            grant,
            AthleteAccessGrant,
        ):
            raise TypeError(
                "grant must be an AthleteAccessGrant."
            )

        row = self._connection.execute(
            select(
                user_athlete_access.c.permission
            ).where(
                user_athlete_access.c.user_id
                == grant.user_id,
                user_athlete_access.c.athlete_id
                == grant.athlete_id,
            )
        ).mappings().one_or_none()

        if row is not None:

            if (
                row["permission"]
                != grant.permission
            ):
                raise ValueError(
                    "Athlete access permission "
                    "cannot be changed silently."
                )

            return

        self._connection.execute(
            insert(
                user_athlete_access
            ).values(
                user_id=grant.user_id,
                athlete_id=grant.athlete_id,
                permission=grant.permission,
            )
        )

    def delete(
        self,
        user_id: str,
        athlete_id: str,
    ) -> None:
        """
        Delete one access grant.
        """

        (
            normalized_user_id,
            normalized_athlete_id,
        ) = self._normalized_key(
            user_id,
            athlete_id,
        )

        result = self._connection.execute(
            delete(
                user_athlete_access
            ).where(
                user_athlete_access.c.user_id
                == normalized_user_id,
                user_athlete_access.c.athlete_id
                == normalized_athlete_id,
            )
        )

        if result.rowcount == 0:
            raise KeyError(
                "Athlete access grant does not exist."
            )

    def list_for_user(
        self,
        user_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return all grants belonging to one user.
        """

        normalized_user_id = (
            self._normalized_value(
                user_id,
                field_name="user_id",
            )
        )

        rows = self._connection.execute(
            select(
                user_athlete_access
            ).where(
                user_athlete_access.c.user_id
                == normalized_user_id
            ).order_by(
                user_athlete_access.c.athlete_id
            )
        ).mappings().all()

        return [
            self._grant_from_row(
                row
            )
            for row in rows
        ]

    def list_for_athlete(
        self,
        athlete_id: str,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return all grants for one athlete.
        """

        normalized_athlete_id = (
            self._normalized_value(
                athlete_id,
                field_name="athlete_id",
            )
        )

        rows = self._connection.execute(
            select(
                user_athlete_access
            ).where(
                user_athlete_access.c.athlete_id
                == normalized_athlete_id
            ).order_by(
                user_athlete_access.c.user_id
            )
        ).mappings().all()

        return [
            self._grant_from_row(
                row
            )
            for row in rows
        ]

    def list(
        self,
    ) -> list[
        AthleteAccessGrant
    ]:
        """
        Return every access grant.
        """

        rows = self._connection.execute(
            select(
                user_athlete_access
            ).order_by(
                user_athlete_access.c.user_id,
                user_athlete_access.c.athlete_id,
            )
        ).mappings().all()

        return [
            self._grant_from_row(
                row
            )
            for row in rows
        ]