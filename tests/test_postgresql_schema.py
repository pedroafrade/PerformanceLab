"""
Tests for the PostgreSQL persistence schema.
"""

from sqlalchemy import (
    CheckConstraint,
)
from sqlalchemy.dialects import (
    postgresql,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)
from sqlalchemy.schema import (
    CreateTable,
)

from performancelab.storage.postgresql_schema import (
    POSTGRESQL_TABLES,
    alpha_invitations,
    alpha_participation_consents,
    athlete_snapshots,
    daily_briefs,
    athletes,
    external_identities,
    metadata,
    training_coach_consents,
    training_coach_usage,
    user_athlete_access,
    users,
)


def column_names(
    table,
):

    return tuple(
        column.name
        for column in table.columns
    )


def primary_key_names(
    table,
):

    return tuple(
        column.name
        for column
        in table.primary_key.columns
    )


def test_defines_expected_postgresql_tables():

    assert set(
        metadata.tables
    ) == {
        "athletes",
        "users",
        "external_identities",
        "user_athlete_access",
        "alpha_invitations",
        "training_coach_consents",
        "training_coach_usage",
        "alpha_participation_consents",
        "athlete_snapshots",
        "daily_briefs",
    }

    assert tuple(
        POSTGRESQL_TABLES
    ) == (
        athletes,
        users,
        external_identities,
        user_athlete_access,
        alpha_invitations,
        training_coach_consents,
        training_coach_usage,
        alpha_participation_consents,
        athlete_snapshots,
        daily_briefs,
    )


def test_athletes_track_current_snapshot_version():

    assert column_names(
        athletes
    ) == (
        "athlete_id",
        "name",
        "current_version",
        "created_at",
        "updated_at",
    )

    assert primary_key_names(
        athletes
    ) == (
        "athlete_id",
    )

    assert (
        athletes.c.current_version
        .nullable
        is False
    )


def test_users_have_unique_email_and_optional_athlete():

    assert column_names(
        users
    ) == (
        "user_id",
        "email",
        "role",
        "athlete_id",
        "created_at",
    )

    assert primary_key_names(
        users
    ) == (
        "user_id",
    )

    assert (
        users.c.athlete_id
        .nullable
        is True
    )

    unique_columns = {
        tuple(
            column.name
            for column
            in constraint.columns
        )
        for constraint
        in users.constraints
        if constraint.__class__.__name__
        == "UniqueConstraint"
    }

    assert (
        "email",
    ) in unique_columns


def test_external_identity_uses_stable_composite_key():

    assert primary_key_names(
        external_identities
    ) == (
        "issuer",
        "subject",
    )

    user_foreign_key = next(
        iter(
            external_identities
            .c
            .user_id
            .foreign_keys
        )
    )

    assert (
        user_foreign_key.target_fullname
        == "users.user_id"
    )

    assert (
        user_foreign_key.ondelete
        == "CASCADE"
    )


def test_access_grant_is_unique_per_user_and_athlete():

    assert primary_key_names(
        user_athlete_access
    ) == (
        "user_id",
        "athlete_id",
    )

    assert (
        user_athlete_access
        .c
        .permission
        .nullable
        is False
    )


def test_athlete_snapshot_uses_jsonb_and_version():

    assert primary_key_names(
        athlete_snapshots
    ) == (
        "athlete_id",
        "version",
    )

    assert isinstance(
        athlete_snapshots.c.payload.type,
        JSONB,
    )

    assert (
        athlete_snapshots
        .c
        .payload
        .nullable
        is False
    )


def test_invitation_email_is_unique():

    unique_columns = {
        tuple(
            column.name
            for column
            in constraint.columns
        )
        for constraint
        in alpha_invitations.constraints
        if constraint.__class__.__name__
        == "UniqueConstraint"
    }

    assert (
        "email",
    ) in unique_columns


def test_schema_contains_domain_value_constraints():

    constrained_tables = (
        athletes,
        users,
        user_athlete_access,
        alpha_invitations,
        training_coach_consents,
        training_coach_usage,
        athlete_snapshots,
    )

    for table in constrained_tables:

        assert any(
            isinstance(
                constraint,
                CheckConstraint,
            )
            for constraint
            in table.constraints
        )


def test_every_table_compiles_for_postgresql():

    dialect = (
        postgresql.dialect()
    )

    statements = tuple(
        str(
            CreateTable(
                table
            ).compile(
                dialect=dialect
            )
        )
        for table
        in metadata.sorted_tables
    )

    assert len(
        statements
    ) == len(
        POSTGRESQL_TABLES
    )

    assert all(
        "CREATE TABLE"
        in statement
        for statement in statements
    )

def test_training_coach_usage_contains_no_payload():

    assert column_names(
        training_coach_usage
    ) == (
        "usage_id",
        "user_id",
        "occurred_at",
        "status",
        "provider",
        "model",
        "error_code",
        "latency_ms",
        "remaining_user_requests",
        "remaining_global_requests",
    )

    assert primary_key_names(
        training_coach_usage
    ) == (
        "usage_id",
    )

    user_foreign_key = next(
        iter(
            training_coach_usage
            .c
            .user_id
            .foreign_keys
        )
    )

    assert (
        user_foreign_key.target_fullname
        == "users.user_id"
    )

    assert (
        user_foreign_key.ondelete
        == "CASCADE"
    )



def test_alpha_participation_consent_schema():

    assert column_names(
        alpha_participation_consents
    ) == (
        "consent_id",
        "user_id",
        "notice_version",
        "accepted_at",
        "withdrawn_at",
    )

    assert primary_key_names(
        alpha_participation_consents
    ) == (
        "consent_id",
    )

    user_foreign_key = next(
        iter(
            alpha_participation_consents
            .c
            .user_id
            .foreign_keys
        )
    )

    assert (
        user_foreign_key.target_fullname
        == "users.user_id"
    )

    assert (
        user_foreign_key.ondelete
        == "CASCADE"
    )

    assert (
        alpha_participation_consents
        .c
        .withdrawn_at
        .nullable
        is True
    )
