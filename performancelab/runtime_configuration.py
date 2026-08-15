"""
PerformanceLab

Validated runtime environment configuration.
"""

from collections.abc import (
    Mapping,
)
from dataclasses import (
    dataclass,
    field,
)
from typing import (
    Literal,
)

from sqlalchemy.engine import (
    make_url,
)
from sqlalchemy.exc import (
    ArgumentError,
)


RuntimeEnvironment = Literal[
    "local",
    "test",
    "alpha",
]


@dataclass(
    frozen=True
)
class RuntimeConfiguration:
    """
    Describe one explicit PerformanceLab runtime environment.

    Database credentials are deliberately excluded from the
    generated representation to prevent accidental logging.
    """

    environment: RuntimeEnvironment = "local"

    database_url: str | None = field(
        default=None,
        repr=False,
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Normalize and validate the configuration.
        """

        if not isinstance(
            self.environment,
            str,
        ):
            raise TypeError(
                "PERFORMANCELAB_ENV must be a string."
            )

        normalized_environment = (
            self.environment
            .strip()
            .lower()
        )

        if normalized_environment not in (
            "local",
            "test",
            "alpha",
        ):
            raise ValueError(
                "PERFORMANCELAB_ENV must be "
                "'local', 'test' or 'alpha'."
            )

        normalized_database_url = (
            self.database_url.strip()
            if isinstance(
                self.database_url,
                str,
            )
            and self.database_url.strip()
            else None
        )

        if (
            self.database_url is not None
            and not isinstance(
                self.database_url,
                str,
            )
        ):
            raise TypeError(
                "DATABASE_URL must be a string or None."
            )

        if (
            normalized_environment
            == "local"
        ):

            if normalized_database_url is not None:
                raise ValueError(
                    "The local environment must use "
                    "the current JSON repositories."
                )

        else:

            if normalized_database_url is None:
                raise RuntimeError(
                    "DATABASE_URL is required in "
                    f"the {normalized_environment} environment."
                )

            normalized_database_url = (
                self._postgresql_url(
                    normalized_database_url
                )
            )

        object.__setattr__(
            self,
            "environment",
            normalized_environment,
        )

        object.__setattr__(
            self,
            "database_url",
            normalized_database_url,
        )

    @classmethod
    def from_mapping(
        cls,
        values: Mapping[
            str,
            object,
        ],
    ):
        """
        Build configuration from environment-style values.
        """

        if not isinstance(
            values,
            Mapping,
        ):
            raise TypeError(
                "Configuration values must be a mapping."
            )

        environment = values.get(
            "PERFORMANCELAB_ENV",
            "local",
        )

        database_url = values.get(
            "DATABASE_URL"
        )

        return cls(
            environment=environment,
            database_url=database_url,
        )

    @property
    def uses_json(
        self,
    ) -> bool:
        """
        Return whether local JSON repositories are allowed.
        """

        return (
            self.environment
            == "local"
        )

    @property
    def uses_postgresql(
        self,
    ) -> bool:
        """
        Return whether PostgreSQL is mandatory.
        """

        return (
            self.environment
            in (
                "test",
                "alpha",
            )
        )

    @staticmethod
    def _postgresql_url(
        value: str,
    ) -> str:
        """
        Validate and normalize a SQLAlchemy PostgreSQL URL.
        """

        try:

            url = make_url(
                value
            )

        except ArgumentError as error:

            raise ValueError(
                "DATABASE_URL is not a valid "
                "database connection URL."
            ) from error

        if (
            url.get_backend_name()
            != "postgresql"
        ):
            raise ValueError(
                "DATABASE_URL must identify "
                "a PostgreSQL database."
            )

        if (
            url.drivername
            == "postgresql"
        ):
            url = url.set(
                drivername=(
                    "postgresql+psycopg"
                )
            )

        if (
            url.drivername
            != "postgresql+psycopg"
        ):
            raise ValueError(
                "DATABASE_URL must use "
                "the Psycopg 3 driver."
            )

        return url.render_as_string(
            hide_password=False
        )