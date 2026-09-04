"""Store explicitly confirmed Daily Brief timezones.

Revision ID: 20260904_04
Revises: 20260904_03
"""

from alembic import op
import sqlalchemy as sa


revision = "20260904_04"
down_revision = "20260904_03"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "daily_brief_timezones",
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("timezone_name", sa.String(length=64), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "length(timezone_name) > 0",
            name=op.f("ck_daily_brief_timezones_timezone_name_not_empty"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            name=op.f("fk_daily_brief_timezones_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id",
            name=op.f("pk_daily_brief_timezones"),
        ),
    )


def downgrade():
    op.drop_table("daily_brief_timezones")
