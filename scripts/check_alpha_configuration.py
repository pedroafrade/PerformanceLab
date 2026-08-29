"""
PerformanceLab

Safe private alpha configuration preflight.
"""

from collections.abc import (
    Mapping,
)
import os
import sys

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)


SUCCESS_MESSAGE = (
    "Alpha runtime configuration is structurally valid."
)

FAILURE_MESSAGE = (
    "Alpha runtime configuration is incomplete or invalid. "
    "Review .env.example without printing secret values."
)


def validate_alpha_configuration(
    values: Mapping[str, object],
) -> bool:
    """
    Validate the core alpha runtime configuration.
    """

    try:

        configuration = (
            RuntimeConfiguration
            .from_mapping(values)
        )

    except (
        TypeError,
        ValueError,
        RuntimeError,
    ):

        return False

    return (
        configuration.environment
        == "alpha"
        and (
            configuration
            .support_contact_email
            is not None
        )
    )


def main(
    values: Mapping[str, object] | None = None,
) -> int:
    """
    Validate configuration without displaying its values.
    """

    configuration_values = (
        os.environ
        if values is None
        else values
    )

    if not validate_alpha_configuration(
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