"""
PerformanceLab

Safe immutable alpha image reference preflight.
"""

from collections.abc import (
    Mapping,
)
import os
import re
import sys


IMAGE_REFERENCE_KEY = (
    "DEPLOYMENT_IMAGE_REFERENCE"
)

SUCCESS_MESSAGE = (
    "Alpha deployment image reference is immutable."
)

FAILURE_MESSAGE = (
    "Alpha deployment image reference is missing "
    "or is not pinned to a sha256 digest."
)

DIGEST_REFERENCE_PATTERN = re.compile(
    r"^[^@\s]+@sha256:[0-9a-fA-F]{64}$"
)


def validate_image_reference(
    value: object,
) -> bool:
    """
    Validate an image reference without displaying it.
    """

    if not isinstance(
        value,
        str,
    ):
        return False

    return bool(
        DIGEST_REFERENCE_PATTERN.fullmatch(
            value.strip()
        )
    )


def main(
    values: Mapping[
        str,
        object,
    ] | None = None,
) -> int:
    """
    Validate the configured deployment image reference.
    """

    configuration = (
        os.environ
        if values is None
        else values
    )

    if not validate_image_reference(
        configuration.get(
            IMAGE_REFERENCE_KEY
        )
    ):

        print(
            FAILURE_MESSAGE,
            file=sys.stderr,
        )

        return 1

    print(
        SUCCESS_MESSAGE
    )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )