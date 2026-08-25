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
from performancelab.retention_policy import (
    AlphaRetentionPolicy,
    RETENTION_SETTING_NAMES,
)
from performancelab.training_coach_usage_limits import (
    TrainingCoachUsageLimits,
)

RuntimeEnvironment = Literal[
    "local",
    "test",
    "alpha",
]

RUNTIME_CONFIGURATION_SETTING_NAMES = (
    "PERFORMANCELAB_ENV",
    "DATABASE_URL",
    "TRAINING_COACH_ENABLED",
    "TRAINING_COACH_USER_DAILY_LIMIT",
    "TRAINING_COACH_GLOBAL_DAILY_LIMIT",
    *RETENTION_SETTING_NAMES.values(),
)

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

    retention_policy: (
        AlphaRetentionPolicy
        | None
    ) = None
    training_coach_enabled: bool = True
    training_coach_user_daily_limit: int = 5
    training_coach_global_daily_limit: int = 50

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

                if (
                    normalized_environment
                    == "alpha"
                ):

                    raise RuntimeError(
                        "DATABASE_URL is required in "
                        "the alpha environment. "
                        "JSON persistence is forbidden "
                        "and no local fallback will be used."
                    )

                raise RuntimeError(
                    "DATABASE_URL is required in "
                    f"the {normalized_environment} environment."
                )

            normalized_database_url = (
                self._postgresql_url(
                    normalized_database_url
                )
            )

        if (
            self.retention_policy
            is not None
            and not isinstance(
                self.retention_policy,
                AlphaRetentionPolicy,
            )
        ):

            raise TypeError(
                "retention_policy must be an "
                "AlphaRetentionPolicy or None."
            )

        if (
            normalized_environment
            == "alpha"
            and self.retention_policy
            is None
        ):

            raise RuntimeError(
                "A complete retention policy is required "
                "in the alpha environment."
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
        training_coach_enabled = (
            self._boolean_setting(
                self.training_coach_enabled,
                field_name=(
                    "TRAINING_COACH_ENABLED"
                ),
            )
        )

        object.__setattr__(
            self,
            "training_coach_enabled",
            training_coach_enabled,
        )
        usage_limits = (
            TrainingCoachUsageLimits(
                user_daily_limit=(
                    self
                    .training_coach_user_daily_limit
                ),
                global_daily_limit=(
                    self
                    .training_coach_global_daily_limit
                ),
            )
        )

        object.__setattr__(
            self,
            (
                "training_coach_"
                "user_daily_limit"
            ),
            usage_limits.user_daily_limit,
        )

        object.__setattr__(
            self,
            (
                "training_coach_"
                "global_daily_limit"
            ),
            usage_limits.global_daily_limit,
        )
    @staticmethod
    def _boolean_setting(
        value,
        *,
        field_name: str,
    ) -> bool:
        """
        Convert an environment setting into a boolean.
        """

        if isinstance(
            value,
            bool,
        ):

            return value

        if not isinstance(
            value,
            str,
        ):

            raise TypeError(
                f"{field_name} must be "
                "true or false."
            )

        normalized_value = (
            value.strip().lower()
        )

        if normalized_value in (
            "true",
            "1",
            "yes",
            "on",
        ):

            return True

        if normalized_value in (
            "false",
            "0",
            "no",
            "off",
        ):

            return False

        raise ValueError(
            f"{field_name} must be "
            "true or false."
        )

    @staticmethod
    def _integer_setting(
        value,
        *,
        field_name: str,
    ) -> int:
        """
        Convert an environment setting into an integer.
        """

        if isinstance(
            value,
            bool,
        ):

            raise TypeError(
                f"{field_name} must be an integer."
            )

        if isinstance(
            value,
            int,
        ):

            return value

        if not isinstance(
            value,
            str,
        ):

            raise TypeError(
                f"{field_name} must be an integer."
            )

        normalized_value = (
            value.strip()
        )

        try:

            return int(
                normalized_value
            )

        except ValueError as error:

            raise ValueError(
                f"{field_name} must be an integer."
            ) from error

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

        normalized_environment = (
            environment.strip().lower()
            if isinstance(
                environment,
                str,
            )
            else environment
        )

        retention_policy = (
            AlphaRetentionPolicy
            .from_mapping(
                values
            )
            if (
                normalized_environment
                == "alpha"
                and database_url is not None
                and (
                    not isinstance(
                        database_url,
                        str,
                    )
                    or database_url.strip()
                )
            )
            else None
        )

        training_coach_enabled = (
            cls._boolean_setting(
                values.get(
                    "TRAINING_COACH_ENABLED",
                    True,
                ),
                field_name=(
                    "TRAINING_COACH_ENABLED"
                ),
            )
        )

        user_daily_limit = (
            cls._integer_setting(
                values.get(
                    (
                        "TRAINING_COACH_"
                        "USER_DAILY_LIMIT"
                    ),
                    5,
                ),
                field_name=(
                    "TRAINING_COACH_"
                    "USER_DAILY_LIMIT"
                ),
            )
        )

        global_daily_limit = (
            cls._integer_setting(
                values.get(
                    (
                        "TRAINING_COACH_"
                        "GLOBAL_DAILY_LIMIT"
                    ),
                    50,
                ),
                field_name=(
                    "TRAINING_COACH_"
                    "GLOBAL_DAILY_LIMIT"
                ),
            )
        )

        return cls(
            environment=environment,
            database_url=database_url,
            retention_policy=(
                retention_policy
            ),
            training_coach_enabled=(
                training_coach_enabled
            ),
            training_coach_user_daily_limit=(
                user_daily_limit
            ),
            training_coach_global_daily_limit=(
                global_daily_limit
            ),
        )

    @property
    def training_coach_usage_limits(
        self,
    ) -> TrainingCoachUsageLimits:
        """
        Return the validated Training Coach limits.
        """

        return TrainingCoachUsageLimits(
            user_daily_limit=(
                self
                .training_coach_user_daily_limit
            ),
            global_daily_limit=(
                self
                .training_coach_global_daily_limit
            ),
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