"""
Integration tests for the complete JSON to SQL migration.

SQLite is used only as an isolated in-memory SQL database.
Production continues to use PostgreSQL and JSONB.
"""

import pytest

from sqlalchemy import (
    create_engine,
    event,
    select,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.exc import (
    IntegrityError,
)
from sqlalchemy.ext.compiler import (
    compiles,
)

from performancelab.alpha_invitation import (
    AlphaInvitation,
)
from performancelab.application.migrate_json_to_postgresql import (
    migrate_json_to_postgresql,
)
from performancelab.athlete import (
    Athlete,
)
from performancelab.athlete_access import (
    AthleteAccessGrant,
)
from performancelab.identity import (
    ExternalIdentityLink,
    User,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.json import (
    athlete_to_dict,
)
from performancelab.storage.postgresql_schema import (
    athlete_snapshots,
    athletes,
    metadata,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


@compiles(
    JSONB,
    "sqlite",
)
def compile_jsonb_for_sqlite(
    element,
    compiler,
    **kwargs,
):
    """
    Allow the temporary SQL database to represent JSONB.

    This changes only the isolated test database.
    """

    return "JSON"


def temporary_sql_engine():
    """
    Create an isolated SQL database with foreign keys enabled.
    """

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    @event.listens_for(
        engine,
        "connect",
    )
    def enable_foreign_keys(
        database_connection,
        connection_record,
    ):

        cursor = (
            database_connection.cursor()
        )

        cursor.execute(
            "PRAGMA foreign_keys=ON"
        )

        cursor.close()

    metadata.create_all(
        engine
    )

    return engine


def postgresql_test_bundle(
    engine,
):
    """
    Build the real PostgreSQL repository implementations over
    the isolated SQL connection.
    """

    def engine_factory(
        database_url,
        **kwargs,
    ):

        return engine

    return build_repository_bundle(
        RuntimeConfiguration(
            environment="test",
            database_url=(
                "postgresql+psycopg://"
                "test:test@localhost/"
                "performancelab_test"
            ),
        ),
        engine_factory=engine_factory,
    )


def json_bundle(
    directory,
):
    """
    Build the real local JSON repositories.
    """

    return build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=directory,
    )


def local_file_contents(
    directory,
):
    """
    Read every local JSON file as unmodified bytes.
    """

    return {
        path.relative_to(
            directory
        ): path.read_bytes()
        for path
        in sorted(
            directory.rglob(
                "*.json"
            )
        )
    }


def populate_complete_json_source(
    source,
):
    """
    Store one connected factual data set in JSON.
    """

    athlete = Athlete(
        athlete_id="athlete-1",
        name="Pedro",
        birth_date=None,
        gender="male",
        height=175,
        weight=70,
        ftp=220,
        max_hr=190,
        resting_hr=48,
        threshold_hr=177,
    )

    user = User(
        user_id="user-1",
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-1",
    )

    identity = ExternalIdentityLink(
        issuer=(
            "https://accounts.google.com"
        ),
        subject="google-subject-1",
        user_id="user-1",
    )

    invitation = AlphaInvitation(
        invitation_id="invitation-1",
        email="pedro@example.com",
        role="athlete",
        athlete_id="athlete-1",
        claimed_by_user_id="user-1",
    )

    grant = AthleteAccessGrant(
        user_id="user-1",
        athlete_id="athlete-1",
        permission="owner",
    )

    source.athlete_repository.save(
        athlete
    )
    source.user_repository.save(
        user
    )
    source.external_identity_repository.save(
        identity
    )
    source.alpha_invitation_repository.save(
        invitation
    )
    source.athlete_access_repository.save(
        grant
    )

    return {
        "athlete": athlete,
        "user": user,
        "identity": identity,
        "invitation": invitation,
        "grant": grant,
    }


def test_complete_json_data_survives_sql_round_trip(
    tmp_path,
):

    source_directory = (
        tmp_path
        / "local-data"
    )

    source = json_bundle(
        source_directory
    )

    expected = (
        populate_complete_json_source(
            source
        )
    )

    json_before = (
        local_file_contents(
            source_directory
        )
    )

    engine = temporary_sql_engine()

    destination = (
        postgresql_test_bundle(
            engine
        )
    )

    try:

        summary = (
            migrate_json_to_postgresql(
                source,
                destination,
            )
        )

        loaded_athlete = (
            destination
            .athlete_repository
            .get(
                "athlete-1"
            )
        )

        assert athlete_to_dict(
            loaded_athlete
        ) == athlete_to_dict(
            expected[
                "athlete"
            ]
        )

        assert (
            destination
            .user_repository
            .get(
                "user-1"
            )
            == expected[
                "user"
            ]
        )

        assert (
            destination
            .external_identity_repository
            .get(
                (
                    "https://"
                    "accounts.google.com"
                ),
                "google-subject-1",
            )
            == expected[
                "identity"
            ]
        )

        assert (
            destination
            .alpha_invitation_repository
            .get(
                "invitation-1"
            )
            == expected[
                "invitation"
            ]
        )

        assert (
            destination
            .athlete_access_repository
            .get(
                "user-1",
                "athlete-1",
            )
            == expected[
                "grant"
            ]
        )

        assert summary.total_records == 5

        assert (
            json_before
            == local_file_contents(
                source_directory
            )
        )

        current_version = (
            destination.connection.execute(
                select(
                    athletes
                    .c
                    .current_version
                ).where(
                    athletes.c.athlete_id
                    == "athlete-1"
                )
            ).scalar_one()
        )

        snapshot_versions = (
            destination.connection.execute(
                select(
                    athlete_snapshots
                    .c
                    .version
                ).where(
                    (
                        athlete_snapshots
                        .c
                        .athlete_id
                        == "athlete-1"
                    )
                )
            ).scalars().all()
        )

        assert current_version == 1
        assert snapshot_versions == [
            1,
        ]

    finally:

        destination.close()
        source.close()


def test_failed_migration_leaves_sql_destination_empty(
    tmp_path,
):

    source_directory = (
        tmp_path
        / "invalid-local-data"
    )

    source = json_bundle(
        source_directory
    )

    source.athlete_repository.save(
        Athlete(
            athlete_id="athlete-1",
            name="Pedro",
        )
    )

    # This link deliberately references a user that does not
    # exist. JSON can contain it, but the SQL foreign key must
    # reject it.
    source.external_identity_repository.save(
        ExternalIdentityLink(
            issuer=(
                "https://accounts.google.com"
            ),
            subject="invalid-subject",
            user_id="missing-user",
        )
    )

    json_before = (
        local_file_contents(
            source_directory
        )
    )

    engine = temporary_sql_engine()

    destination = (
        postgresql_test_bundle(
            engine
        )
    )

    try:

        with pytest.raises(
            IntegrityError
        ):

            migrate_json_to_postgresql(
                source,
                destination,
            )

        assert (
            destination
            .athlete_repository
            .list()
            == []
        )

        assert (
            destination
            .user_repository
            .list()
            == []
        )

        assert (
            destination
            .external_identity_repository
            .list()
            == []
        )

        assert (
            destination
            .alpha_invitation_repository
            .list()
            == []
        )

        assert (
            destination
            .athlete_access_repository
            .list()
            == []
        )

        assert (
            json_before
            == local_file_contents(
                source_directory
            )
        )

    finally:

        destination.close()
        source.close()