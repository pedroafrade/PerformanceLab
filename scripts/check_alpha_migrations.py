"""
PerformanceLab

Safe private alpha migration preflight.
"""

from collections.abc import (
    Mapping,
)
import os
import sys

from alembic.config import (
    Config,
)
from alembic.runtime.migration import (
    MigrationContext,
)
from alembic.script import (
    ScriptDirectory,
)
from sqlalchemy import (
    create_engine,
)

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)


SUCCESS_MESSAGE = (
    "Alpha database migrations are current."
)

FAILURE_MESSAGE = (
    "Alpha database migrations are not current."
)


def validate_alpha_migrations(
    values: Mapping[str, object],
    *,
    engine_factory=create_engine,
    config_factory=Config,
    script_factory=ScriptDirectory.from_config,
    context_factory=MigrationContext.configure,
) -> bool:
    """
    Compare database revisions with repository heads.
    """

    engine = None

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

        alembic_config = config_factory(
            "alembic.ini"
        )

        script_directory = script_factory(
            alembic_config
        )

        expected_heads = set(
            script_directory.get_heads()
        )

        if not expected_heads:

            return False

        engine = engine_factory(
            configuration.database_url,
            pool_pre_ping=True,
        )

        with engine.connect() as connection:

            migration_context = context_factory(
                connection
            )

            current_heads = set(
                migration_context
                .get_current_heads()
            )

        return (
            current_heads
            == expected_heads
        )

    except Exception:

        return False

    finally:

        if engine is not None:

            try:

                engine.dispose()

            except Exception:

                pass


def main(
    values: Mapping[str, object] | None = None,
) -> int:
    """
    Check revisions without displaying connection details.
    """

    configuration_values = (
        os.environ
        if values is None
        else values
    )

    if not validate_alpha_migrations(
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