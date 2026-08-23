"""
Tests for the JSON to PostgreSQL migration service.
"""

from contextlib import (
    contextmanager,
)

import pytest

from performancelab.application.migrate_json_to_postgresql import (
    DestinationNotEmptyError,
    SourceDataEmptyError,
    migrate_json_to_postgresql,
)


class FakeRepository:
    """
    Minimal repository used to verify migration behaviour.
    """

    def __init__(
        self,
        records=(),
        *,
        name="repository",
        save_log=None,
    ) -> None:

        self._records = list(
            records
        )
        self._name = name
        self._save_log = (
            save_log
            if save_log is not None
            else []
        )

    def list(
        self,
    ):

        return list(
            self._records
        )

    def save(
        self,
        record,
    ) -> None:

        self._save_log.append(
            (
                self._name,
                record,
            )
        )

        self._records.append(
            record
        )


class FakeBundle:
    """
    Repository bundle with a visible transaction context.
    """

    def __init__(
        self,
        *,
        uses_postgresql,
        athletes=(),
        users=(),
        identities=(),
        invitations=(),
        grants=(),
        save_log=None,
    ) -> None:

        self.uses_postgresql = (
            uses_postgresql
        )
        self.transaction_calls = []
        self.save_log = (
            save_log
            if save_log is not None
            else []
        )

        self.athlete_repository = (
            FakeRepository(
                athletes,
                name="athletes",
                save_log=self.save_log,
            )
        )
        self.user_repository = (
            FakeRepository(
                users,
                name="users",
                save_log=self.save_log,
            )
        )
        self.external_identity_repository = (
            FakeRepository(
                identities,
                name="identities",
                save_log=self.save_log,
            )
        )
        self.alpha_invitation_repository = (
            FakeRepository(
                invitations,
                name="invitations",
                save_log=self.save_log,
            )
        )
        self.athlete_access_repository = (
            FakeRepository(
                grants,
                name="grants",
                save_log=self.save_log,
            )
        )

    @contextmanager
    def transaction(
        self,
    ):

        self.transaction_calls.append(
            "enter"
        )

        try:

            yield self

        except Exception:

            self.transaction_calls.append(
                "rollback"
            )

            raise

        else:

            self.transaction_calls.append(
                "commit"
            )


def source_bundle():

    return FakeBundle(
        uses_postgresql=False,
        athletes=(
            "athlete-1",
        ),
        users=(
            "user-1",
        ),
        identities=(
            "identity-1",
        ),
        invitations=(
            "invitation-1",
        ),
        grants=(
            "grant-1",
        ),
    )


def empty_destination():

    return FakeBundle(
        uses_postgresql=True
    )


def test_migrates_every_record_in_foreign_key_order():

    source = source_bundle()
    destination = empty_destination()

    summary = (
        migrate_json_to_postgresql(
            source,
            destination,
        )
    )

    assert destination.save_log == [
        (
            "athletes",
            "athlete-1",
        ),
        (
            "users",
            "user-1",
        ),
        (
            "identities",
            "identity-1",
        ),
        (
            "invitations",
            "invitation-1",
        ),
        (
            "grants",
            "grant-1",
        ),
    ]

    assert (
        destination.transaction_calls
        == [
            "enter",
            "commit",
        ]
    )

    assert summary.athletes == 1
    assert summary.users == 1
    assert (
        summary.external_identities
        == 1
    )
    assert (
        summary.alpha_invitations
        == 1
    )
    assert (
        summary.athlete_access_grants
        == 1
    )
    assert summary.total_records == 5


def test_rejects_non_empty_postgresql_destination():

    source = source_bundle()

    destination = FakeBundle(
        uses_postgresql=True,
        athletes=(
            "existing-athlete",
        ),
    )

    with pytest.raises(
        DestinationNotEmptyError,
        match=(
            "already contains "
            "PerformanceLab data"
        ),
    ):

        migrate_json_to_postgresql(
            source,
            destination,
        )

    assert destination.save_log == []

    assert (
        destination.transaction_calls
        == [
            "enter",
            "rollback",
        ]
    )


def test_rejects_empty_json_source():

    source = FakeBundle(
        uses_postgresql=False
    )

    destination = empty_destination()

    with pytest.raises(
        SourceDataEmptyError,
        match=(
            "No local JSON records"
        ),
    ):

        migrate_json_to_postgresql(
            source,
            destination,
        )

    assert (
        destination.transaction_calls
        == []
    )


def test_rejects_postgresql_as_source():

    source = FakeBundle(
        uses_postgresql=True,
        athletes=(
            "athlete-1",
        ),
    )

    destination = empty_destination()

    with pytest.raises(
        ValueError,
        match=(
            "source must use "
            "local JSON"
        ),
    ):

        migrate_json_to_postgresql(
            source,
            destination,
        )


def test_rejects_json_as_destination():

    source = source_bundle()

    destination = FakeBundle(
        uses_postgresql=False
    )

    with pytest.raises(
        ValueError,
        match=(
            "destination must use "
            "PostgreSQL"
        ),
    ):

        migrate_json_to_postgresql(
            source,
            destination,
        )