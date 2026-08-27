"""
PerformanceLab

Safe private alpha database preflight.
"""

from collections.abc import (
    Mapping,
)
import os
import sys

from performancelab.health import (
    check_application_health,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


SUCCESS_MESSAGE = (
    "Alpha database connection is ready."
)

FAILURE_MESSAGE = (
    "Alpha database connection is unavailable."
)


def validate_alpha_database(
    values: Mapping[str, object],
    *,
    bundle_builder=build_repository_bundle,
    health_checker=check_application_health,
) -> bool:
    """
    Verify PostgreSQL without displaying connection details.
    """

    repository_bundle = None

    try:

        configuration = (
            RuntimeConfiguration
            .from_mapping(values)
        )

        if (
            configuration.environment
            != "alpha"
        ):

            return False

        repository_bundle = bundle_builder(
            configuration
        )

        health = health_checker(
            configuration,
            repository_bundle,
        )

        return health.ready

    except Exception:

        return False

    finally:

        if repository_bundle is not None:

            try:

                repository_bundle.close()

            except Exception:

                pass


def main(
    values: Mapping[str, object] | None = None,
) -> int:
    """
    Verify the database without printing its URL.
    """

    configuration_values = (
        os.environ
        if values is None
        else values
    )

    if not validate_alpha_database(
        configuration_values
    ):

        print(
            FAILURE_MESSAGE,
            file=sys.stderr,
        )

        return 1

    print(SUCCESS_MESSAGE)

    return 0


if __name__ == "__main__":

    raise SystemExit(main())