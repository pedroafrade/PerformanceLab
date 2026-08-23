"""
PerformanceLab

Safe migration from local JSON repositories to PostgreSQL.
"""

from dataclasses import (
    dataclass,
)


class SourceDataEmptyError(
    RuntimeError
):
    """
    Raised when no local records are available to migrate.
    """


class DestinationNotEmptyError(
    RuntimeError
):
    """
    Raised when PostgreSQL already contains application data.
    """


@dataclass(
    frozen=True
)
class JSONMigrationSummary:
    """
    Factual count of the records copied to PostgreSQL.
    """

    athletes: int
    users: int
    external_identities: int
    alpha_invitations: int
    athlete_access_grants: int

    @property
    def total_records(
        self,
    ) -> int:
        """
        Return the total number of migrated records.
        """

        return (
            self.athletes
            + self.users
            + self.external_identities
            + self.alpha_invitations
            + self.athlete_access_grants
        )


@dataclass(
    frozen=True
)
class _JSONMigrationData:
    """
    Immutable snapshot read from all local repositories.
    """

    athletes: tuple
    users: tuple
    external_identities: tuple
    alpha_invitations: tuple
    athlete_access_grants: tuple

    @property
    def total_records(
        self,
    ) -> int:
        """
        Return the total number of source records.
        """

        return (
            len(
                self.athletes
            )
            + len(
                self.users
            )
            + len(
                self.external_identities
            )
            + len(
                self.alpha_invitations
            )
            + len(
                self.athlete_access_grants
            )
        )


def _read_source_data(
    source_bundle,
) -> _JSONMigrationData:
    """
    Read every local record before opening a destination
    transaction.

    Reading everything first ensures malformed JSON is detected
    before PostgreSQL is changed.
    """

    data = _JSONMigrationData(
        athletes=tuple(
            source_bundle
            .athlete_repository
            .list()
        ),
        users=tuple(
            source_bundle
            .user_repository
            .list()
        ),
        external_identities=tuple(
            source_bundle
            .external_identity_repository
            .list()
        ),
        alpha_invitations=tuple(
            source_bundle
            .alpha_invitation_repository
            .list()
        ),
        athlete_access_grants=tuple(
            source_bundle
            .athlete_access_repository
            .list()
        ),
    )

    if data.total_records == 0:

        raise SourceDataEmptyError(
            "No local JSON records were found. "
            "The migration was not started."
        )

    return data


def _destination_record_count(
    destination_bundle,
) -> int:
    """
    Count all records already stored in PostgreSQL.
    """

    return sum(
        len(
            repository.list()
        )
        for repository in (
            destination_bundle
            .athlete_repository,
            destination_bundle
            .user_repository,
            destination_bundle
            .external_identity_repository,
            destination_bundle
            .alpha_invitation_repository,
            destination_bundle
            .athlete_access_repository,
        )
    )


def _save_all(
    repository,
    records: tuple,
) -> None:
    """
    Save every record using its existing repository contract.
    """

    for record in records:

        repository.save(
            record
        )


def migrate_json_to_postgresql(
    source_bundle,
    destination_bundle,
) -> JSONMigrationSummary:
    """
    Copy one complete local JSON data set to empty PostgreSQL.

    The local source is never changed. PostgreSQL must be empty
    and every destination write runs in one transaction.
    """

    if source_bundle.uses_postgresql:

        raise ValueError(
            "The migration source must use local JSON "
            "repositories."
        )

    if not destination_bundle.uses_postgresql:

        raise ValueError(
            "The migration destination must use PostgreSQL."
        )

    source_data = _read_source_data(
        source_bundle
    )

    with destination_bundle.transaction():

        if (
            _destination_record_count(
                destination_bundle
            )
            != 0
        ):

            raise DestinationNotEmptyError(
                "PostgreSQL already contains PerformanceLab "
                "data. Nothing was copied."
            )

        # Foreign-key order:
        # athletes before users, identities, invitations and
        # access grants.
        _save_all(
            destination_bundle
            .athlete_repository,
            source_data.athletes,
        )

        _save_all(
            destination_bundle
            .user_repository,
            source_data.users,
        )

        _save_all(
            destination_bundle
            .external_identity_repository,
            source_data.external_identities,
        )

        _save_all(
            destination_bundle
            .alpha_invitation_repository,
            source_data.alpha_invitations,
        )

        _save_all(
            destination_bundle
            .athlete_access_repository,
            source_data.athlete_access_grants,
        )

        destination_count = (
            _destination_record_count(
                destination_bundle
            )
        )

        if (
            destination_count
            != source_data.total_records
        ):

            raise RuntimeError(
                "PostgreSQL record verification failed. "
                "The migration will be rolled back."
            )

    return JSONMigrationSummary(
        athletes=len(
            source_data.athletes
        ),
        users=len(
            source_data.users
        ),
        external_identities=len(
            source_data.external_identities
        ),
        alpha_invitations=len(
            source_data.alpha_invitations
        ),
        athlete_access_grants=len(
            source_data.athlete_access_grants
        ),
    )