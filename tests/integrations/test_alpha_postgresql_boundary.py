"""
Acceptance tests for the private-alpha persistence boundary.
"""

import pytest

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
from performancelab.storage.json_user_repository import (
    JsonUserRepository,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


JSON_REPOSITORY_TYPES = (
    JsonAthleteRepository,
    JsonUserRepository,
    JsonExternalIdentityRepository,
    JsonAlphaInvitationRepository,
    JsonAthleteAccessRepository,
)
ALPHA_RETENTION_SETTINGS = {
    "RETENTION_INACTIVE_ACCOUNT_DAYS": "90",
    "RETENTION_INACTIVITY_NOTICE_DAYS": "14",
    "RETENTION_TRAINING_COACH_USAGE_DAYS": "30",
    "RETENTION_CONSENT_EVIDENCE_DAYS": "0",
    "RETENTION_UNUSED_INVITATION_DAYS": "14",
    "RETENTION_EXPIRED_INVITATION_DAYS": "7",
    "RETENTION_APPLICATION_LOG_DAYS": "14",
    "RETENTION_ERROR_ALERT_DAYS": "30",
    "RETENTION_BACKUP_DAYS": "14",
    "RETENTION_SUPPORT_REQUEST_DAYS": "90",
    "RETENTION_POST_ALPHA_DAYS": "30",
}

def test_alpha_without_database_cannot_fall_back_to_json():

    with pytest.raises(
        RuntimeError,
        match=(
            "JSON persistence is forbidden"
        ),
    ):

        RuntimeConfiguration.from_mapping(
            {
                "PERFORMANCELAB_ENV": (
                    "alpha"
                ),
            }
        )


def test_alpha_builds_no_local_json_repositories(
    tmp_path,
):

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

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                "PERFORMANCELAB_ENV": (
                    "alpha"
                ),
                "DATABASE_URL": (
                    "postgresql+psycopg://"
                    "user:secret@db.example.com/"
                    "performancelab"
                ),
                **ALPHA_RETENTION_SETTINGS,
            }
        )
    )

    bundle = build_repository_bundle(
        configuration,
        data_directory=tmp_path,
        engine_factory=engine_factory,
    )

    try:

        repositories = (
            bundle.athlete_repository,
            bundle.user_repository,
            bundle.external_identity_repository,
            bundle.alpha_invitation_repository,
            bundle.athlete_access_repository,
        )

        assert bundle.uses_postgresql is True

        assert not any(
            isinstance(
                repository,
                JSON_REPOSITORY_TYPES,
            )
            for repository
            in repositories
        )

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

        assert (
            list(
                tmp_path.iterdir()
            )
            == []
        )

    finally:

        bundle.close()


def test_local_development_still_uses_json(
    tmp_path,
):

    configuration = (
        RuntimeConfiguration
        .from_mapping(
            {
                "PERFORMANCELAB_ENV": (
                    "local"
                ),
            }
        )
    )

    bundle = build_repository_bundle(
        configuration,
        data_directory=tmp_path,
    )

    repositories = (
        bundle.athlete_repository,
        bundle.user_repository,
        bundle.external_identity_repository,
        bundle.alpha_invitation_repository,
        bundle.athlete_access_repository,
    )

    assert bundle.uses_postgresql is False

    assert all(
        isinstance(
            repository,
            JSON_REPOSITORY_TYPES,
        )
        for repository
        in repositories
    )