"""
PerformanceLab

PostgreSQL implementation of the user repository.
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

from performancelab.identity import (
    User,
)
from performancelab.storage.postgresql_schema import (
    users,
)


class PostgreSQLUserRepository:
    """
    Store users in PostgreSQL.

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
    def _user_from_row(
        row,
    ) -> User:
        """
        Convert one database row into a domain user.
        """

        return User(
            user_id=row["user_id"],
            email=row["email"],
            role=row["role"],
            athlete_id=row["athlete_id"],
        )

    def save(
        self,
        user: User,
    ) -> None:
        """
        Save a new user or update an existing user.
        """

        if not isinstance(
            user,
            User,
        ):
            raise TypeError(
                "user must be a User."
            )

        existing = self._connection.execute(
            select(
                users.c.user_id
            ).where(
                users.c.user_id
                == user.user_id
            )
        ).first()

        values = {
            "email": user.email,
            "role": user.role,
            "athlete_id": user.athlete_id,
        }

        if existing is None:

            self._connection.execute(
                insert(
                    users
                ).values(
                    user_id=user.user_id,
                    **values,
                )
            )

            return

        self._connection.execute(
            update(
                users
            ).where(
                users.c.user_id
                == user.user_id
            ).values(
                **values
            )
        )

    def get(
        self,
        user_id: str,
    ) -> User:
        """
        Return a user by ID.
        """

        normalized_user_id = (
            self._normalized_text(
                user_id,
                field_name="user_id",
            )
        )

        row = self._connection.execute(
            select(
                users
            ).where(
                users.c.user_id
                == normalized_user_id
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                f"User not found: {normalized_user_id}"
            )

        return self._user_from_row(
            row
        )

    def get_by_email(
        self,
        email: str,
    ) -> User:
        """
        Return a user by email address.

        Email comparison is case-insensitive.
        """

        normalized_email = (
            self._normalized_text(
                email,
                field_name="email",
            ).lower()
        )

        row = self._connection.execute(
            select(
                users
            ).where(
                users.c.email
                == normalized_email
            )
        ).mappings().one_or_none()

        if row is None:
            raise KeyError(
                f"User not found: {normalized_email}"
            )

        return self._user_from_row(
            row
        )

    def list(
        self,
    ) -> list[
        User
    ]:
        """
        Return all users ordered by email.
        """

        rows = self._connection.execute(
            select(
                users
            ).order_by(
                users.c.email
            )
        ).mappings().all()

        return [
            self._user_from_row(
                row
            )
            for row in rows
        ]

    def delete(
        self,
        user_id: str,
    ) -> None:
        """
        Delete a user by ID.
        """

        normalized_user_id = (
            self._normalized_text(
                user_id,
                field_name="user_id",
            )
        )

        result = self._connection.execute(
            delete(
                users
            ).where(
                users.c.user_id
                == normalized_user_id
            )
        )

        if result.rowcount == 0:
            raise KeyError(
                f"User not found: {normalized_user_id}"
            )

    @staticmethod
    def _normalized_text(
        value: str,
        *,
        field_name: str,
    ) -> str:
        """
        Normalize and validate a text lookup key.
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