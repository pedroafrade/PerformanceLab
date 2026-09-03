"""Daily Brief cache and leases. Revision 20260904_01, after 20260825_02."""

from alembic import op
import sqlalchemy as sa


revision = "20260904_01"
down_revision = "20260825_02"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "daily_briefs",
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("athlete_id", sa.String(36), nullable=False),
        sa.Column("saved_key", sa.String(64)),
        sa.Column("saved_payload", sa.JSON()),
        sa.Column("lease_key", sa.String(64)),
        sa.Column("lease_token", sa.String(36)),
        sa.Column("lease_until", sa.DateTime(timezone=True)),
        sa.Column("retry_after", sa.DateTime(timezone=True)),
        sa.PrimaryKeyConstraint("user_id", "athlete_id", name="pk_daily_briefs"),
        sa.ForeignKeyConstraint(["user_id"], ["users.user_id"],
                                ondelete="CASCADE", name="fk_daily_briefs_user"),
        sa.ForeignKeyConstraint(["athlete_id"], ["athletes.athlete_id"],
                                ondelete="CASCADE", name="fk_daily_briefs_athlete"),
    )


def downgrade():
    op.drop_table("daily_briefs")
