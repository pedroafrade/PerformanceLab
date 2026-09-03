"""Shared Training Coach quota reservations; no provider/runtime activation."""

from alembic import op
import sqlalchemy as sa


revision = "20260904_03"
down_revision = "20260904_02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "training_coach_quota_reservations",
        sa.Column("request_id", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("utc_day", sa.Date(), nullable=False),
        sa.Column("purpose", sa.String(20), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("reserved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("request_id", name=op.f("pk_training_coach_quota_reservations")),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"], ondelete="CASCADE",
                                name=op.f("fk_training_coach_quota_reservations_user_id_users")),
        sa.CheckConstraint("purpose IN ('activity', 'daily_brief')",
                           name=op.f("ck_training_coach_quota_reservations_purpose")),
        sa.CheckConstraint("state IN ('reserved', 'generated', 'released')",
                           name=op.f("ck_training_coach_quota_reservations_state")),
    )


def downgrade():
    # Loses reservation/audit state. Disable generation before any downgrade.
    op.drop_table("training_coach_quota_reservations")
