"""
PerformanceLab

Application health verification tests.
"""

from sqlalchemy import (
    create_engine,
)

from performancelab.health import (
    check_application_health,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.repository_factory import (
    RepositoryBundle,
)


def repository_bundle(
    *,
    engine=None,
    connection=None,
):
    return RepositoryBundle(
        athlete_repository=object(),
        user_repository=object(),
        external_identity_repository=object(),
        alpha_invitation_repository=object(),
        alpha_participation_consent_repository=object(),
        athlete_access_repository=object(),
        training_coach_consent_repository=object(),
        training_coach_usage_repository=object(),
        engine=engine,
        connection=connection,
    )


def test_local_environment_is_ready_without_database():

    health = check_application_health(
        RuntimeConfiguration(
            environment="local"
        ),
        repository_bundle(),
    )

    assert health.ready is True
    assert health.configuration == "ready"
    assert health.database == "not_required"


def test_local_environment_rejects_postgresql_bundle():

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )
    connection = engine.connect()

    try:

        health = check_application_health(
            RuntimeConfiguration(
                environment="local"
            ),
            repository_bundle(
                engine=engine,
                connection=connection,
            ),
        )

        assert health.ready is False
        assert health.database == "unavailable"

    finally:

        connection.close()
        engine.dispose()


def test_database_health_executes_safe_query():

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )
    connection = engine.connect()

    try:

        health = check_application_health(
            RuntimeConfiguration(
                environment="test",
                database_url=(
                    "postgresql+psycopg://"
                    "user:secret@db.example.com/"
                    "performancelab"
                ),
            ),
            repository_bundle(
                engine=engine,
                connection=connection,
            ),
        )

        assert health.ready is True
        assert health.configuration == "ready"
        assert health.database == "ready"

    finally:

        connection.close()
        engine.dispose()


def test_database_health_failure_has_safe_result():

    class FailingEngine:

        def connect(self):

            raise RuntimeError(
                "secret database information"
            )

    engine = FailingEngine()

    bundle = repository_bundle(
        engine=engine,
        connection=object(),
    )

    health = check_application_health(
        RuntimeConfiguration(
            environment="test",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@db.example.com/"
                "performancelab"
            ),
        ),
        bundle,
    )

    assert health.ready is False
    assert health.configuration == "ready"
    assert health.database == "unavailable"
    assert "secret" not in repr(
        health
    )