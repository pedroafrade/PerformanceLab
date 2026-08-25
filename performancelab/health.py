"""
PerformanceLab

Application and database health verification.
"""

from dataclasses import (
    dataclass,
)

from sqlalchemy import (
    text,
)

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.repository_factory import (
    RepositoryBundle,
)


@dataclass(
    frozen=True
)
class ApplicationHealth:
    """
    Safe application readiness result.

    No connection details, credentials or exception messages
    are included.
    """

    ready: bool
    configuration: str
    database: str


def check_application_health(
    configuration: RuntimeConfiguration,
    repository_bundle: RepositoryBundle,
) -> ApplicationHealth:
    """
    Confirm that configuration and persistence are ready.
    """

    if not isinstance(
        configuration,
        RuntimeConfiguration,
    ):
        raise TypeError(
            "configuration must be a RuntimeConfiguration."
        )

    if not isinstance(
        repository_bundle,
        RepositoryBundle,
    ):
        raise TypeError(
            "repository_bundle must be a RepositoryBundle."
        )

    if configuration.uses_json:

        ready = (
            not repository_bundle
            .uses_postgresql
        )

        return ApplicationHealth(
            ready=ready,
            configuration="ready",
            database=(
                "not_required"
                if ready
                else "unavailable"
            ),
        )

    if (
        not configuration.uses_postgresql
        or not repository_bundle
        .uses_postgresql
        or repository_bundle.engine is None
    ):

        return ApplicationHealth(
            ready=False,
            configuration="ready",
            database="unavailable",
        )

    try:

        with (
            repository_bundle
            .engine
            .connect()
        ) as connection:

            result = connection.execute(
                text(
                    "SELECT 1"
                )
            )

            database_ready = (
                result.scalar_one()
                == 1
            )

    except Exception:

        database_ready = False

    return ApplicationHealth(
        ready=database_ready,
        configuration="ready",
        database=(
            "ready"
            if database_ready
            else "unavailable"
        ),
    )