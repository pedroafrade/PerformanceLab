"""
Add Training Coach operational metadata.

Revision ID: 20260825_01
Revises: 20260824_03
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


revision: str = "20260825_01"

down_revision: Optional[
    Union[
        str,
        Sequence[str],
    ]
] = "20260824_03"

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
    Add non-sensitive operational metadata.
    """

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "provider",
            sa.String(
                length=100
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "model",
            sa.String(
                length=200
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "error_code",
            sa.String(
                length=100
            ),
            nullable=True,
        ),
    )

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "latency_ms",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "remaining_user_requests",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "training_coach_usage",
        sa.Column(
            "remaining_global_requests",
            sa.Integer(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """
    Remove Training Coach operational metadata.
    """

    op.drop_column(
        "training_coach_usage",
        "remaining_global_requests",
    )

    op.drop_column(
        "training_coach_usage",
        "remaining_user_requests",
    )

    op.drop_column(
        "training_coach_usage",
        "latency_ms",
    )

    op.drop_column(
        "training_coach_usage",
        "error_code",
    )

    op.drop_column(
        "training_coach_usage",
        "model",
    )

    op.drop_column(
        "training_coach_usage",
        "provider",
    )