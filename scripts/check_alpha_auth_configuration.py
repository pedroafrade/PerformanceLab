"""
PerformanceLab

Safe Streamlit OIDC configuration preflight.
"""

from collections.abc import (
    Mapping,
)
from pathlib import (
    Path,
)
import sys
import tomllib


DEFAULT_AUTH_CONFIGURATION_PATH = Path(
    "/app/.streamlit/secrets.toml"
)

REQUIRED_AUTH_SETTINGS = (
    "redirect_uri",
    "cookie_secret",
    "client_id",
    "client_secret",
    "server_metadata_url",
)

SUCCESS_MESSAGE = (
    "Alpha authentication configuration "
    "is structurally valid."
)

FAILURE_MESSAGE = (
    "Alpha authentication configuration "
    "is incomplete or invalid."
)


def validate_auth_configuration(
    values: Mapping[str, object],
) -> bool:
    """
    Validate required Streamlit OIDC settings.
    """

    if not isinstance(
        values,
        Mapping,
    ):

        return False

    auth_values = values.get(
        "auth"
    )

    if not isinstance(
        auth_values,
        Mapping,
    ):

        return False

    return all(
        isinstance(
            auth_values.get(setting_name),
            str,
        )
        and bool(
            auth_values[
                setting_name
            ].strip()
        )
        for setting_name
        in REQUIRED_AUTH_SETTINGS
    )


def load_auth_configuration(
    path: Path,
) -> Mapping[str, object] | None:
    """
    Load TOML without displaying its values.
    """

    try:

        with path.open("rb") as file:

            return tomllib.load(
                file
            )

    except (
        OSError,
        tomllib.TOMLDecodeError,
    ):

        return None


def main(
    path: Path = DEFAULT_AUTH_CONFIGURATION_PATH,
) -> int:
    """
    Validate the mounted OIDC configuration safely.
    """

    values = load_auth_configuration(
        path
    )

    if (
        values is None
        or not validate_auth_configuration(
            values
        )
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