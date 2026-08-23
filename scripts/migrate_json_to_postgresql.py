"""
Copy local PerformanceLab JSON data to empty PostgreSQL.

This script never deletes or changes the local JSON files.
"""

import argparse
import os

from pathlib import (
    Path,
)

from performancelab.application.migrate_json_to_postgresql import (
    migrate_json_to_postgresql,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


def arguments():
    """
    Read the explicit migration confirmation.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Copy local PerformanceLab JSON data to "
            "an empty PostgreSQL database."
        )
    )

    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Explicitly authorize the copy. "
            "Local JSON files are preserved."
        ),
    )

    parser.add_argument(
        "--data-directory",
        type=Path,
        default=Path(
            "data"
        ),
        help=(
            "Directory containing the local JSON "
            "repositories."
        ),
    )

    return parser.parse_args()


def main() -> int:
    """
    Execute the explicitly authorized migration.
    """

    options = arguments()

    if not options.execute:

        print(
            "Migration not started. "
            "Use --execute only after checking the "
            "PostgreSQL destination."
        )

        return 2

    database_url = os.getenv(
        "DATABASE_URL"
    )

    if not database_url:

        raise RuntimeError(
            "DATABASE_URL must be configured before "
            "starting the migration."
        )

    source_bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=(
            options.data_directory
        ),
    )

    destination_bundle = (
        build_repository_bundle(
            RuntimeConfiguration(
                environment="alpha",
                database_url=database_url,
            )
        )
    )

    try:

        summary = (
            migrate_json_to_postgresql(
                source_bundle,
                destination_bundle,
            )
        )

    finally:

        destination_bundle.close()
        source_bundle.close()

    print(
        "Migration completed successfully."
    )
    print(
        f"Athletes: {summary.athletes}"
    )
    print(
        f"Users: {summary.users}"
    )
    print(
        "External identities: "
        f"{summary.external_identities}"
    )
    print(
        "Alpha invitations: "
        f"{summary.alpha_invitations}"
    )
    print(
        "Athlete access grants: "
        f"{summary.athlete_access_grants}"
    )
    print(
        f"Total records: {summary.total_records}"
    )
    print(
        "Local JSON files were preserved."
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )