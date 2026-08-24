"""
Create Training Coach usage persistence.

Revision ID: 20260824_03
Revises: 20260824_02
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


revision: str = "20260824_03"

down_revision: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = "20260824_02"

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
    Create factual Training Coach usage records.
    """

    op.create_table(
        "training_coach_usage",
        sa.Column(
            "usage_id",
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
            "occurred_at",
            sa.DateTime(
                timezone=True
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(
                length=20
            ),
            nullable=False,
        ),
        sa.CheckConstraint(
            (
                "status IN "
                "('generated', 'failed')"
            ),
            name=(
                "ck_training_coach_usage_"
                "status"
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
                "fk_training_coach_usage_"
                "user_id_users"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "usage_id",
            name=(
                "pk_training_coach_usage"
            ),
        ),
    )


def downgrade() -> None:
    """
    Remove Training Coach usage persistence.
    """

    op.drop_table(
        "training_coach_usage"
    )