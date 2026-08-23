"""
PerformanceLab

Repository selection by runtime environment.
"""
from contextlib import (
    contextmanager,
)
from dataclasses import (
    dataclass,
    field,
)

from pathlib import (
    Path,
)
from typing import (
    Callable,
)

from sqlalchemy import (
    create_engine,
)
from sqlalchemy.engine import (
    Connection,
    Engine,
)

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)
from performancelab.storage.json_athlete_repository import (
    JsonAthleteRepository,
)
from performancelab.storage.json_external_identity_repository import (
    JsonExternalIdentityRepository,
)
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)
from performancelab.storage.postgresql_alpha_invitation_repository import (
    PostgreSQLAlphaInvitationRepository,
)
from performancelab.storage.postgresql_athlete_access_repository import (
    PostgreSQLAthleteAccessRepository,
)
from performancelab.storage.postgresql_athlete_repository import (
    PostgreSQLAthleteRepository,
)
from performancelab.storage.postgresql_external_identity_repository import (
    PostgreSQLExternalIdentityRepository,
)
from performancelab.storage.postgresql_user_repository import (
    PostgreSQLUserRepository,
)


@dataclass(
    frozen=True
)
class RepositoryBundle:
    """
    Repositories used by one application runtime.

    PostgreSQL resources are retained so that their lifecycle
    can later be managed transactionally.
    """

    athlete_repository: object
    user_repository: object
    external_identity_repository: object
    alpha_invitation_repository: object
    athlete_access_repository: object

    engine: Engine | None = field(
        default=None,
        repr=False,
    )
    connection: Connection | None = field(
        default=None,
        repr=False,
    )

    @property
    def uses_postgresql(
        self,
    ) -> bool:
        """
        Return whether this bundle uses PostgreSQL.
        """

        return (
            self.engine is not None
            and self.connection is not None
        )
    @contextmanager
    def transaction(
        self,
    ):
        """
        Group related repository operations.

        JSON repositories preserve their current local
        compensation behaviour. PostgreSQL operations share one
        database transaction and are committed only when the
        complete operation succeeds.
        """

        if self.connection is None:

            yield self

            return

        if self.connection.in_transaction():

            raise RuntimeError(
                "A PostgreSQL transaction is already active."
            )

        with self.connection.begin():

            yield self

    def close(
        self,
    ) -> None:
        """
        Release owned PostgreSQL resources.

        Local JSON bundles do not own external resources.
        """

        if self.connection is not None:

            self.connection.close()

        if self.engine is not None:

            self.engine.dispose()


def build_repository_bundle(
    configuration: RuntimeConfiguration,
    *,
    data_directory: str | Path = "data",
    engine_factory: Callable = create_engine,
) -> RepositoryBundle:
    """
    Build the repositories required by one runtime.
    """

    if not isinstance(
        configuration,
        RuntimeConfiguration,
    ):
        raise TypeError(
            "configuration must be a RuntimeConfiguration."
        )

    data_directory = Path(
        data_directory
    )

    if configuration.uses_json:

        return RepositoryBundle(
            athlete_repository=(
                JsonAthleteRepository(
                    data_directory
                    / "athletes"
                )
            ),
            user_repository=(
                JsonUserRepository(
                    data_directory
                    / "users"
                )
            ),
            external_identity_repository=(
                JsonExternalIdentityRepository(
                    data_directory
                    / "external_identities"
                )
            ),
            alpha_invitation_repository=(
                JsonAlphaInvitationRepository(
                    data_directory
                    / "alpha_invitations"
                )
            ),
            athlete_access_repository=(
                JsonAthleteAccessRepository(
                    data_directory
                    / "athlete_access"
                )
            ),
        )

    if not configuration.uses_postgresql:
        raise RuntimeError(
            "The runtime environment does not have "
            "a supported persistence mode."
        )

    engine = engine_factory(
        configuration.database_url,
        pool_pre_ping=True,
    )

    try:

        connection = engine.connect()

    except Exception:

        engine.dispose()
        raise

    return RepositoryBundle(
        athlete_repository=(
            PostgreSQLAthleteRepository(
                connection
            )
        ),
        user_repository=(
            PostgreSQLUserRepository(
                connection
            )
        ),
        external_identity_repository=(
            PostgreSQLExternalIdentityRepository(
                connection
            )
        ),
        alpha_invitation_repository=(
            PostgreSQLAlphaInvitationRepository(
                connection
            )
        ),
        athlete_access_repository=(
            PostgreSQLAthleteAccessRepository(
                connection
            )
        ),
        engine=engine,
        connection=connection,
    )