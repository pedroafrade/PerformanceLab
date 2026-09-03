"""Add purpose/token metadata without changing existing successful-use counts."""

from alembic import op
import sqlalchemy as sa


revision = "20260904_02"
down_revision = "20260904_01"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("training_coach_usage", sa.Column(
        "purpose", sa.String(20), nullable=False, server_default="activity"))
    for name in ("prompt_tokens", "output_tokens", "total_tokens"):
        op.add_column("training_coach_usage", sa.Column(name, sa.Integer(), nullable=True))
        op.create_check_constraint(op.f("ck_training_coach_usage_" + name + "_nonnegative"),
                                   "training_coach_usage", f"{name} IS NULL OR {name} >= 0")
    op.create_check_constraint(op.f("ck_training_coach_usage_purpose"), "training_coach_usage",
                               "purpose IN ('activity', 'daily_brief')")


def downgrade():
    # Rollback removes the newly added metadata, not the original usage events.
    op.drop_constraint(op.f("ck_training_coach_usage_purpose"), "training_coach_usage", type_="check")
    for name in ("total_tokens", "output_tokens", "prompt_tokens"):
        op.drop_constraint(op.f("ck_training_coach_usage_" + name + "_nonnegative"),
                           "training_coach_usage", type_="check")
        op.drop_column("training_coach_usage", name)
    op.drop_column("training_coach_usage", "purpose")
