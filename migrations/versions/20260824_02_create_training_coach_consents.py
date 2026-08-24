"""
Create Training Coach consent persistence.

Revision ID: 20260824_02
Revises: 20260823_01
Create Date: 2026-08-24
"""

from typing import (
    Optional,
    Sequence,
    Union,
)

from alembic import (
    op,
)
import sqlalchemy as sa


revision: str = "20260824_02"

down_revision: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = "20260823_01"

branch_labels: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = None

depends_on: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = None


def upgrade() -> None:
    """
    Create versioned Training Coach consent records.
    """

    op.create_table(
        "training_coach_consents",
        sa.Column(
            "consent_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.String(
                length=36
            ),
            nullable=False,
        ),
        sa.Column(
            "purpose",
            sa.String(
                length=50
            ),
            nullable=False,
        ),
        sa.Column(
            "policy_version",
            sa.String(
                length=100
            ),
            nullable=False,
        ),
        sa.Column(
            "granted_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.Column(
            "withdrawn_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=True,
        ),
        sa.CheckConstraint(
            "purpose = 'training-coach'",
            name=(
                "ck_training_coach_consents_"
                "purpose"
            ),
        ),
        sa.ForeignKeyConstraint(
            [
                "user_id",
            ],
            [
                "users.user_id",
            ],
            name=(
                "fk_training_coach_consents_"
                "user_id_users"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "consent_id",
            name=(
                "pk_training_coach_consents"
            ),
        ),
    )


def downgrade() -> None:
    """
    Remove Training Coach consent persistence.
    """

    op.drop_table(
        "training_coach_consents"
    )