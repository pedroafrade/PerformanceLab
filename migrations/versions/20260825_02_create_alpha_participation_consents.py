"""
Create private alpha participation consent persistence.

Revision ID: 20260825_02
Revises: 20260825_01
Create Date: 2026-08-25
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


revision: str = "20260825_02"

down_revision: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = "20260825_01"

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
    Create versioned private alpha consent records.
    """

    op.create_table(
        "alpha_participation_consents",
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
            "notice_version",
            sa.String(
                length=100
            ),
            nullable=False,
        ),
        sa.Column(
            "accepted_at",
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
        sa.ForeignKeyConstraint(
            [
                "user_id",
            ],
            [
                "users.user_id",
            ],
            name=(
                "fk_alpha_participation_"
                "consents_user_id_users"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "consent_id",
            name=(
                "pk_alpha_participation_"
                "consents"
            ),
        ),
    )


def downgrade() -> None:
    """
    Remove private alpha consent persistence.
    """

    op.drop_table(
        "alpha_participation_consents"
    )