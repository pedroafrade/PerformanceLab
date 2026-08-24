"""
Tests for repository selection by runtime environment.
"""

from sqlalchemy import (
    create_engine,
)

from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.json_alpha_invitation_repository import (
    JsonAlphaInvitationRepository,
)
from performancelab.storage.json_athlete_access_repository import (
    JsonAthleteAccessRepository,
)
from performancelab.storage.json_athlete_repository import (
    JsonAthleteRepository,
)
from performancelab.storage.json_external_identity_repository import (
    JsonExternalIdentityRepository,
)
from performancelab.storage.json_training_coach_consent_repository import (
    JsonTrainingCoachConsentRepository,
)
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)
from performancelab.storage.postgresql_alpha_invitation_repository import (
    PostgreSQLAlphaInvitationRepository,
)
from performancelab.storage.postgresql_athlete_access_repository import (
    PostgreSQLAthleteAccessRepository,
)
from performancelab.storage.postgresql_athlete_repository import (
    PostgreSQLAthleteRepository,
)
from performancelab.storage.postgresql_external_identity_repository import (
    PostgreSQLExternalIdentityRepository,
)
from performancelab.storage.postgresql_training_coach_consent_repository import (
    PostgreSQLTrainingCoachConsentRepository,
)
from performancelab.storage.postgresql_user_repository import (
    PostgreSQLUserRepository,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


def test_local_environment_selects_json_repositories(
    tmp_path,
):

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=tmp_path,
    )

    assert isinstance(
        bundle.athlete_repository,
        JsonAthleteRepository,
    )
    assert isinstance(
        bundle.user_repository,
        JsonUserRepository,
    )
    assert isinstance(
        bundle.external_identity_repository,
        JsonExternalIdentityRepository,
    )
    assert isinstance(
        bundle.alpha_invitation_repository,
        JsonAlphaInvitationRepository,
    )
    assert isinstance(
        bundle.athlete_access_repository,
        JsonAthleteAccessRepository,
    )
    assert isinstance(
        bundle.training_coach_consent_repository,
        JsonTrainingCoachConsentRepository,
    )

    assert bundle.uses_postgresql is False
    assert bundle.engine is None
    assert bundle.connection is None


def test_local_environment_uses_expected_directories(
    tmp_path,
):

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=tmp_path,
    )

    assert (
        bundle.athlete_repository.directory
        == tmp_path / "athletes"
    )

    assert (
        bundle.user_repository._directory
        == tmp_path / "users"
    )

    assert (
        bundle
        .external_identity_repository
        ._directory
        == tmp_path
        / "external_identities"
    )

    assert (
        bundle
        .alpha_invitation_repository
        ._directory
        == tmp_path
        / "alpha_invitations"
    )

    assert (
        bundle
        .athlete_access_repository
        ._directory
        == tmp_path
        / "athlete_access"
    )
    assert (
        bundle
        .training_coach_consent_repository
        ._directory
        == tmp_path
        / "training_coach_consents"
    )


def test_local_environment_does_not_create_database_engine(
    tmp_path,
):

    calls = []

    def engine_factory(
        *args,
        **kwargs,
    ):

        calls.append(
            (
                args,
                kwargs,
            )
        )

        raise AssertionError(
            "Database engine must not be created locally."
        )

    build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=tmp_path,
        engine_factory=engine_factory,
    )

    assert calls == []


def test_alpha_environment_selects_postgresql_repositories():

    calls = []

    def engine_factory(
        database_url,
        **kwargs,
    ):

        calls.append(
            (
                database_url,
                kwargs,
            )
        )

        return create_engine(
            "sqlite+pysqlite:///:memory:"
        )

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="alpha",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@db.example.com/"
                "performancelab"
            ),
        ),
        engine_factory=engine_factory,
    )

    try:

        assert isinstance(
            bundle.athlete_repository,
            PostgreSQLAthleteRepository,
        )
        assert isinstance(
            bundle.user_repository,
            PostgreSQLUserRepository,
        )
        assert isinstance(
            bundle.external_identity_repository,
            PostgreSQLExternalIdentityRepository,
        )
        assert isinstance(
            bundle.alpha_invitation_repository,
            PostgreSQLAlphaInvitationRepository,
        )
        assert isinstance(
            bundle.athlete_access_repository,
            PostgreSQLAthleteAccessRepository,
        )
        assert isinstance(
            bundle.training_coach_consent_repository,
            PostgreSQLTrainingCoachConsentRepository,
        )

        assert bundle.uses_postgresql is True

        assert calls == [
            (
                (
                    "postgresql+psycopg://"
                    "user:secret@db.example.com/"
                    "performancelab"
                ),
                {
                    "pool_pre_ping": True,
                },
            )
        ]

    finally:

        bundle.close()


def test_test_environment_also_selects_postgresql():

    def engine_factory(
        database_url,
        **kwargs,
    ):

        return create_engine(
            "sqlite+pysqlite:///:memory:"
        )

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="test",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@db.example.com/"
                "performancelab_test"
            ),
        ),
        engine_factory=engine_factory,
    )

    try:

        assert bundle.uses_postgresql is True

        assert isinstance(
            bundle.athlete_repository,
            PostgreSQLAthleteRepository,
        )

    finally:

        bundle.close()


def test_close_releases_postgresql_connection():

    def engine_factory(
        database_url,
        **kwargs,
    ):

        return create_engine(
            "sqlite+pysqlite:///:memory:"
        )

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="alpha",
            database_url=(
                "postgresql+psycopg://"
                "user:secret@db.example.com/"
                "performancelab"
            ),
        ),
        engine_factory=engine_factory,
    )

    connection = bundle.connection

    assert connection.closed is False

    bundle.close()

    assert connection.closed is True