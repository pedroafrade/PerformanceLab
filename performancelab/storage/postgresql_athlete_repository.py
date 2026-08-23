"""
PerformanceLab

PostgreSQL athlete snapshot repository.
"""

from sqlalchemy import (
    and_,
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.engine import (
    Connection,
)

from performancelab.athlete import (
    Athlete,
)
from performancelab.storage.concurrency import (
    ConcurrentAthleteUpdateError,
)
from performancelab.storage.json import (
    athlete_from_dict,
    athlete_to_dict,
)
from performancelab.storage.postgresql_schema import (
    athlete_snapshots,
    athletes,
)


_REPOSITORY_VERSION_ATTRIBUTE = (
    "_performancelab_repository_version"
)


class PostgreSQLAthleteRepository:
    """
    Store complete athlete aggregates as versioned snapshots.

    Every loaded athlete carries the version from which it was
    reconstructed. Saving succeeds only while that version is
    still current in the database.

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
    def _normalized_athlete_id(
        athlete_id: str,
    ) -> str:
        """
        Normalize and validate an athlete identifier.
        """

        if not isinstance(
            athlete_id,
            str,
        ):
            raise TypeError(
                "athlete_id must be a string."
            )

        normalized_athlete_id = (
            athlete_id.strip()
        )

        if not normalized_athlete_id:
            raise ValueError(
                "athlete_id cannot be empty."
            )

        return normalized_athlete_id

    @staticmethod
    def _mark_version(
        athlete: Athlete,
        version: int,
    ) -> Athlete:
        """
        Record the factual database version on a loaded athlete.

        This internal value is not included in the athlete JSON
        payload and is not shown in the user interface.
        """

        setattr(
            athlete,
            _REPOSITORY_VERSION_ATTRIBUTE,
            version,
        )

        return athlete

    @staticmethod
    def _expected_version(
        athlete: Athlete,
    ) -> int | None:
        """
        Return the version from which an athlete was loaded.
        """

        version = getattr(
            athlete,
            _REPOSITORY_VERSION_ATTRIBUTE,
            None,
        )

        if (
            version is not None
            and (
                not isinstance(
                    version,
                    int,
                )
                or isinstance(
                    version,
                    bool,
                )
                or version < 1
            )
        ):
            raise ValueError(
                "Athlete repository version is invalid."
            )

        return version

    @classmethod
    def _athlete_from_payload(
        cls,
        payload,
        *,
        version: int,
    ) -> Athlete:
        """
        Rebuild and version an athlete from a stored snapshot.
        """

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "Athlete snapshot payload must be a dictionary."
            )

        athlete = athlete_from_dict(
            payload
        )

        return cls._mark_version(
            athlete,
            version,
        )

    def get(
        self,
        athlete_id: str,
    ) -> Athlete:
        """
        Return the current version of one athlete.
        """

        normalized_athlete_id = (
            self._normalized_athlete_id(
                athlete_id
            )
        )

        row = self._connection.execute(
            select(
                athletes.c.current_version,
                athlete_snapshots.c.payload,
            ).select_from(
                athletes.join(
                    athlete_snapshots,
                    and_(
                        athlete_snapshots.c.athlete_id
                        == athletes.c.athlete_id,
                        athlete_snapshots.c.version
                        == athletes.c.current_version,
                    ),
                )
            ).where(
                athletes.c.athlete_id
                == normalized_athlete_id
            )
        ).mappings().one_or_none()

        if row is None:
            raise FileNotFoundError(
                f"Athlete {normalized_athlete_id!r} "
                "does not exist"
            )

        return self._athlete_from_payload(
            row["payload"],
            version=row["current_version"],
        )

    def list(
        self,
    ) -> list[
        Athlete
    ]:
        """
        Return the current version of every athlete.
        """

        rows = self._connection.execute(
            select(
                athletes.c.current_version,
                athlete_snapshots.c.payload,
            ).select_from(
                athletes.join(
                    athlete_snapshots,
                    and_(
                        athlete_snapshots.c.athlete_id
                        == athletes.c.athlete_id,
                        athlete_snapshots.c.version
                        == athletes.c.current_version,
                    ),
                )
            ).order_by(
                athletes.c.athlete_id
            )
        ).mappings().all()

        return [
            self._athlete_from_payload(
                row["payload"],
                version=(
                    row["current_version"]
                ),
            )
            for row in rows
        ]

    def save(
        self,
        athlete: Athlete,
    ) -> None:
        """
        Save an athlete if its loaded version is still current.
        """

        if not isinstance(
            athlete,
            Athlete,
        ):
            raise TypeError(
                "athlete must be an Athlete."
            )

        payload = athlete_to_dict(
            athlete
        )

        expected_version = (
            self._expected_version(
                athlete
            )
        )

        current_version = (
            self._connection.execute(
                select(
                    athletes.c.current_version
                ).where(
                    athletes.c.athlete_id
                    == athlete.athlete_id
                )
            ).scalar_one_or_none()
        )

        if current_version is None:

            new_version = 1

            self._connection.execute(
                insert(
                    athletes
                ).values(
                    athlete_id=(
                        athlete.athlete_id
                    ),
                    name=athlete.name,
                    current_version=(
                        new_version
                    ),
                )
            )

            self._connection.execute(
                insert(
                    athlete_snapshots
                ).values(
                    athlete_id=(
                        athlete.athlete_id
                    ),
                    version=new_version,
                    payload=payload,
                )
            )

            self._mark_version(
                athlete,
                new_version,
            )

            return

        if expected_version is None:

            raise ConcurrentAthleteUpdateError(
                athlete.athlete_id,
                expected_version=None,
                actual_version=(
                    current_version
                ),
            )

        new_version = (
            expected_version + 1
        )

        result = self._connection.execute(
            update(
                athletes
            ).where(
                athletes.c.athlete_id
                == athlete.athlete_id,
                athletes.c.current_version
                == expected_version,
            ).values(
                name=athlete.name,
                current_version=new_version,
                updated_at=func.now(),
            )
        )

        if result.rowcount == 0:

            actual_version = (
                self._connection.execute(
                    select(
                        athletes.c.current_version
                    ).where(
                        athletes.c.athlete_id
                        == athlete.athlete_id
                    )
                ).scalar_one()
            )

            raise ConcurrentAthleteUpdateError(
                athlete.athlete_id,
                expected_version=(
                    expected_version
                ),
                actual_version=(
                    actual_version
                ),
            )

        self._connection.execute(
            insert(
                athlete_snapshots
            ).values(
                athlete_id=(
                    athlete.athlete_id
                ),
                version=new_version,
                payload=payload,
            )
        )

        self._mark_version(
            athlete,
            new_version,
        )

    def delete(
        self,
        athlete_id: str,
    ) -> None:
        """
        Delete an athlete and its snapshots.
        """

        normalized_athlete_id = (
            self._normalized_athlete_id(
                athlete_id
            )
        )

        self._connection.execute(
            delete(
                athlete_snapshots
            ).where(
                athlete_snapshots.c.athlete_id
                == normalized_athlete_id
            )
        )

        result = self._connection.execute(
            delete(
                athletes
            ).where(
                athletes.c.athlete_id
                == normalized_athlete_id
            )
        )

        if result.rowcount == 0:
            raise FileNotFoundError(
                f"Athlete {normalized_athlete_id!r} "
                "does not exist"
            )