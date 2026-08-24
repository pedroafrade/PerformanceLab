"""
PerformanceLab

SQLAlchemy Core metadata for PostgreSQL persistence.
"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
)


NAMING_CONVENTION = {
    "ix": (
        "ix_%(column_0_label)s"
    ),
    "uq": (
        "uq_%(table_name)s_"
        "%(column_0_name)s"
    ),
    "ck": (
        "ck_%(table_name)s_"
        "%(constraint_name)s"
    ),
    "fk": (
        "fk_%(table_name)s_"
        "%(column_0_name)s_"
        "%(referred_table_name)s"
    ),
    "pk": (
        "pk_%(table_name)s"
    ),
}


metadata = MetaData(
    naming_convention=(
        NAMING_CONVENTION
    )
)


athletes = Table(
    "athletes",
    metadata,
    Column(
        "athlete_id",
        String(36),
        primary_key=True,
    ),
    Column(
        "name",
        String(200),
        nullable=False,
    ),
    Column(
        "current_version",
        Integer,
        nullable=False,
        server_default="1",
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint(
        "current_version >= 1",
        name="current_version_positive",
    ),
)


users = Table(
    "users",
    metadata,
    Column(
        "user_id",
        String(36),
        primary_key=True,
    ),
    Column(
        "email",
        String(320),
        nullable=False,
    ),
    Column(
        "role",
        String(20),
        nullable=False,
    ),
    Column(
        "athlete_id",
        String(36),
        ForeignKey(
            "athletes.athlete_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    UniqueConstraint(
        "email",
    ),
    CheckConstraint(
        "role IN ('athlete', 'coach')",
        name="role",
    ),
)


external_identities = Table(
    "external_identities",
    metadata,
    Column(
        "issuer",
        String(512),
        primary_key=True,
    ),
    Column(
        "subject",
        String(255),
        primary_key=True,
    ),
    Column(
        "user_id",
        String(36),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
)


user_athlete_access = Table(
    "user_athlete_access",
    metadata,
    Column(
        "user_id",
        String(36),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "athlete_id",
        String(36),
        ForeignKey(
            "athletes.athlete_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "permission",
        String(20),
        nullable=False,
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint(
        "permission IN ('owner', 'coach')",
        name="permission",
    ),
)


alpha_invitations = Table(
    "alpha_invitations",
    metadata,
    Column(
        "invitation_id",
        String(36),
        primary_key=True,
    ),
    Column(
        "email",
        String(320),
        nullable=False,
    ),
    Column(
        "role",
        String(20),
        nullable=False,
    ),
    Column(
        "athlete_id",
        String(36),
        ForeignKey(
            "athletes.athlete_id",
            ondelete="CASCADE",
        ),
        nullable=True,
    ),
    Column(
        "claimed_by_user_id",
        String(36),
        ForeignKey(
            "users.user_id",
            ondelete="SET NULL",
        ),
        nullable=True,
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    UniqueConstraint(
        "email",
    ),
    CheckConstraint(
        "role IN ('athlete', 'coach')",
        name="role",
    ),
    CheckConstraint(
        (
            "role <> 'athlete' "
            "OR athlete_id IS NOT NULL"
        ),
        name="athlete_invitation_has_athlete",
    ),
)

training_coach_consents = Table(
    "training_coach_consents",
    metadata,
    Column(
        "consent_id",
        String(36),
        primary_key=True,
    ),
    Column(
        "user_id",
        String(36),
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
    ),
    Column(
        "purpose",
        String(50),
        nullable=False,
    ),
    Column(
        "policy_version",
        String(100),
        nullable=False,
    ),
    Column(
        "granted_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
    ),
    Column(
        "withdrawn_at",
        DateTime(
            timezone=True
        ),
        nullable=True,
    ),
    CheckConstraint(
        "purpose = 'training-coach'",
        name="purpose",
    ),
)

athlete_snapshots = Table(
    "athlete_snapshots",
    metadata,
    Column(
        "athlete_id",
        String(36),
        ForeignKey(
            "athletes.athlete_id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    ),
    Column(
        "version",
        Integer,
        primary_key=True,
    ),
    Column(
        "payload",
        JSONB,
        nullable=False,
    ),
    Column(
        "created_at",
        DateTime(
            timezone=True
        ),
        nullable=False,
        server_default=func.now(),
    ),
    CheckConstraint(
        "version >= 1",
        name="version_positive",
    ),
)


POSTGRESQL_TABLES = (
    athletes,
    users,
    external_identities,
    user_athlete_access,
    alpha_invitations,
    training_coach_consents,
    athlete_snapshots,
)