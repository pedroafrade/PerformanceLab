"""
Tests for PostgreSQL repository transactions.
"""

import pytest

from sqlalchemy import (
    create_engine,
)

from performancelab.identity import (
    ExternalIdentityLink,
    User,
)
from performancelab.runtime_configuration import (
    RuntimeConfiguration,
)
from performancelab.storage.postgresql_schema import (
    external_identities,
    metadata,
    users,
)
from performancelab.storage.repository_factory import (
    build_repository_bundle,
)


def postgresql_bundle():

    engine = create_engine(
        "sqlite+pysqlite:///:memory:"
    )

    metadata.create_all(
        engine,
        tables=(
            users,
            external_identities,
        ),
    )

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
                "user:secret@db.example.com/"
                "performancelab_test"
            ),
        ),
        engine_factory=engine_factory,
    )


def coach_user():

    return User(
        user_id="user-1",
        email="coach@example.com",
        role="coach",
    )


def identity_link():

    return ExternalIdentityLink(
        issuer="https://accounts.google.com",
        subject="google-subject-1",
        user_id="user-1",
    )


def test_transaction_commits_all_related_changes():

    bundle = postgresql_bundle()

    try:

        with bundle.transaction():

            bundle.user_repository.save(
                coach_user()
            )

            bundle.external_identity_repository.save(
                identity_link()
            )

        assert (
            bundle.user_repository.get(
                "user-1"
            ).email
            == "coach@example.com"
        )

        assert (
            bundle
            .external_identity_repository
            .get(
                "https://accounts.google.com",
                "google-subject-1",
            )
            .user_id
            == "user-1"
        )

    finally:

        bundle.close()


def test_transaction_rolls_back_every_change_on_failure():

    bundle = postgresql_bundle()

    try:

        with pytest.raises(
            RuntimeError,
            match="simulated provisioning failure",
        ):

            with bundle.transaction():

                bundle.user_repository.save(
                    coach_user()
                )

                bundle.external_identity_repository.save(
                    identity_link()
                )

                raise RuntimeError(
                    "simulated provisioning failure"
                )

        assert (
            bundle.user_repository.list()
            == []
        )

        assert (
            bundle
            .external_identity_repository
            .list()
            == []
        )

    finally:

        bundle.close()


def test_rejects_nested_transaction():

    bundle = postgresql_bundle()

    try:

        with bundle.transaction():

            with pytest.raises(
                RuntimeError,
                match=(
                    "transaction is already active"
                ),
            ):

                with bundle.transaction():

                    pass

    finally:

        bundle.close()


def test_local_transaction_context_remains_available(
    tmp_path,
):

    bundle = build_repository_bundle(
        RuntimeConfiguration(
            environment="local"
        ),
        data_directory=tmp_path,
    )

    with bundle.transaction() as active_bundle:

        assert active_bundle is bundle

        bundle.user_repository.save(
            coach_user()
        )

    assert (
        bundle.user_repository.get(
            "user-1"
        ).email
        == "coach@example.com"
    )