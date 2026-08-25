"""
Tests for explicit runtime environment configuration.
"""

import pytest

from performancelab.retention_policy import (
    AlphaRetentionPolicy,
)

from performancelab.runtime_configuration import (
    RUNTIME_CONFIGURATION_SETTING_NAMES,
    RuntimeConfiguration,
)

def alpha_retention_values() -> dict[
    str,
    str,
]:

    return {
        "RETENTION_INACTIVE_ACCOUNT_DAYS": "90",
        "RETENTION_INACTIVITY_NOTICE_DAYS": "14",
        "RETENTION_TRAINING_COACH_USAGE_DAYS": "30",
        "RETENTION_CONSENT_EVIDENCE_DAYS": "0",
        "RETENTION_UNUSED_INVITATION_DAYS": "14",
        "RETENTION_EXPIRED_INVITATION_DAYS": "7",
        "RETENTION_APPLICATION_LOG_DAYS": "14",
        "RETENTION_ERROR_ALERT_DAYS": "30",
        "RETENTION_BACKUP_DAYS": "14",
        "RETENTION_SUPPORT_REQUEST_DAYS": "30",
        "RETENTION_POST_ALPHA_DAYS": "30",
    }


def alpha_retention_policy() -> (
    AlphaRetentionPolicy
):

    return (
        AlphaRetentionPolicy
        .from_mapping(
            alpha_retention_values()
        )
    )

def test_defaults_to_local_json_environment():

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {}
        )
    )

    assert (
        configuration.environment
        == "local"
    )

    assert (
        configuration.database_url
        is None
    )

    assert configuration.uses_json is True

    assert (
        configuration.uses_postgresql
        is False
    )


def test_normalizes_environment_name():

    configuration = RuntimeConfiguration(
        environment=" ALPHA ",
        database_url=(
            "postgresql+psycopg://"
            "user:secret@db.example.com/"
            "performancelab"
        ),
        retention_policy=(
            alpha_retention_policy()
        ),
    )

    assert (
        configuration.environment
        == "alpha"
    )


@pytest.mark.parametrize(
    "environment",
    (
        "test",
        "alpha",
    ),
)
def test_remote_environment_requires_database_url(
    environment,
):

    with pytest.raises(
        RuntimeError,
        match="DATABASE_URL is required",
    ):
        RuntimeConfiguration(
            environment=environment,
        )


def test_rejects_database_url_in_local_environment():

    with pytest.raises(
        ValueError,
        match="local environment",
    ):
        RuntimeConfiguration(
            environment="local",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@localhost/"
                "performancelab"
            ),
        )


def test_normalizes_generic_postgresql_url_to_psycopg():

    configuration = RuntimeConfiguration(
        environment="alpha",
        database_url=(
            "postgresql://"
            "user:secret@db.example.com/"
            "performancelab"
        ),
        retention_policy=(
            alpha_retention_policy()
        ),
    )

    assert configuration.database_url == (
        "postgresql+psycopg://"
        "user:secret@db.example.com/"
        "performancelab"
    )


def test_accepts_explicit_psycopg_url():

    database_url = (
        "postgresql+psycopg://"
        "user:secret@db.example.com/"
        "performancelab"
    )

    configuration = RuntimeConfiguration(
        environment="test",
        database_url=database_url,
    )

    assert (
        configuration.database_url
        == database_url
    )

    assert (
        configuration.uses_postgresql
        is True
    )

    assert (
        configuration.uses_json
        is False
    )


def test_rejects_non_postgresql_database():

    with pytest.raises(
        ValueError,
        match="PostgreSQL",
    ):
        RuntimeConfiguration(
            environment="alpha",
            database_url=(
                "sqlite:///performancelab.db"
            ),
        )


def test_rejects_unsupported_environment():

    with pytest.raises(
        ValueError,
        match=(
            "must be 'local', 'test' or 'alpha'"
        ),
    ):
        RuntimeConfiguration(
            environment="production",
        )


def test_database_password_is_hidden_from_repr():

    configuration = RuntimeConfiguration(
        environment="alpha",
        database_url=(
            "postgresql+psycopg://"
            "user:super-secret-password"
            "@db.example.com/performancelab"
        ),
        retention_policy=(
            alpha_retention_policy()
        ),
    )

    representation = repr(
        configuration
    )

    assert (
        "super-secret-password"
        not in representation
    )

    assert (
        "database_url"
        not in representation
    )


def test_rejects_invalid_configuration_collection():

    with pytest.raises(
        TypeError,
        match="must be a mapping",
    ):
        RuntimeConfiguration.from_mapping(
            None
        )

def test_defaults_training_coach_limits():

    configuration = RuntimeConfiguration(
        environment="local"
    )

    assert (
        configuration
        .training_coach_user_daily_limit
        == 5
    )

    assert (
        configuration
        .training_coach_global_daily_limit
        == 50
    )


def test_reads_training_coach_limits_from_mapping():

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                (
                    "TRAINING_COACH_"
                    "USER_DAILY_LIMIT"
                ): "3",
                (
                    "TRAINING_COACH_"
                    "GLOBAL_DAILY_LIMIT"
                ): "20",
            }
        )
    )

    assert (
        configuration
        .training_coach_user_daily_limit
        == 3
    )

    assert (
        configuration
        .training_coach_global_daily_limit
        == 20
    )

    assert (
        configuration
        .training_coach_usage_limits
        .user_daily_limit
        == 3
    )


def test_rejects_non_integer_training_coach_limit():

    with pytest.raises(
        ValueError,
        match="must be an integer",
    ):

        RuntimeConfiguration.from_mapping(
            {
                (
                    "TRAINING_COACH_"
                    "USER_DAILY_LIMIT"
                ): "five",
            }
        )


def test_rejects_user_limit_above_global_limit():

    with pytest.raises(
        ValueError,
        match="cannot exceed",
    ):

        RuntimeConfiguration.from_mapping(
            {
                (
                    "TRAINING_COACH_"
                    "USER_DAILY_LIMIT"
                ): "20",
                (
                    "TRAINING_COACH_"
                    "GLOBAL_DAILY_LIMIT"
                ): "10",
            }
        )



def test_training_coach_is_enabled_by_default():

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {}
        )
    )

    assert (
        configuration
        .training_coach_enabled
        is True
    )


@pytest.mark.parametrize(
    "configured_value",
    (
        "false",
        "0",
        "no",
        "off",
    ),
)
def test_can_disable_training_coach(
    configured_value,
):

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                "TRAINING_COACH_ENABLED": (
                    configured_value
                ),
            }
        )
    )

    assert (
        configuration
        .training_coach_enabled
        is False
    )


@pytest.mark.parametrize(
    "configured_value",
    (
        "true",
        "1",
        "yes",
        "on",
    ),
)
def test_can_enable_training_coach(
    configured_value,
):

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                "TRAINING_COACH_ENABLED": (
                    configured_value
                ),
            }
        )
    )

    assert (
        configuration
        .training_coach_enabled
        is True
    )


def test_rejects_invalid_training_coach_setting():

    with pytest.raises(
        ValueError,
        match=(
            "TRAINING_COACH_ENABLED "
            "must be true or false"
        ),
    ):

        RuntimeConfiguration.from_mapping(
            {
                "TRAINING_COACH_ENABLED": (
                    "sometimes"
                ),
            }
        )

def test_alpha_environment_requires_retention_policy():

    with pytest.raises(
        RuntimeError,
        match=(
            "complete retention policy is required"
        ),
    ):

        RuntimeConfiguration(
            environment="alpha",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@db.example.com/"
                "performancelab"
            ),
        )


def test_alpha_mapping_requires_retention_settings():

    with pytest.raises(
        RuntimeError,
        match=(
            "Missing private alpha retention settings"
        ),
    ):

        RuntimeConfiguration.from_mapping(
            {
                "PERFORMANCELAB_ENV": "alpha",
                "DATABASE_URL": (
                    "postgresql+psycopg://"
                    "user:secret@db.example.com/"
                    "performancelab"
                ),
            }
        )


def test_alpha_mapping_builds_retention_policy():

    values = {
        "PERFORMANCELAB_ENV": "alpha",
        "DATABASE_URL": (
            "postgresql+psycopg://"
            "user:secret@db.example.com/"
            "performancelab"
        ),
        **alpha_retention_values(),
    }

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            values
        )
    )

    assert isinstance(
        configuration.retention_policy,
        AlphaRetentionPolicy,
    )

    assert (
        configuration
        .retention_policy
        .backup_days
        == 14
    )


def test_local_environment_does_not_require_retention_policy():

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                "PERFORMANCELAB_ENV": "local",
            }
        )
    )

    assert (
        configuration.retention_policy
        is None
    )

def test_runtime_configuration_exposes_retention_settings():

    expected_settings = {
        "PERFORMANCELAB_ENV",
        "DATABASE_URL",
        "TRAINING_COACH_ENABLED",
        "TRAINING_COACH_USER_DAILY_LIMIT",
        "TRAINING_COACH_GLOBAL_DAILY_LIMIT",
        *alpha_retention_values().keys(),
    }

    assert set(
        RUNTIME_CONFIGURATION_SETTING_NAMES
    ) == expected_settings