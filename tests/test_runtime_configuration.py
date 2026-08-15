"""
Tests for explicit runtime environment configuration.
"""

import pytest

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
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