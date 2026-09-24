"""Allow athlete profiles to be created when invitations are claimed.

Revision ID: 20260924_01
Revises: 20260904_04
"""

from alembic import op


revision = "20260924_01"
down_revision = "20260904_04"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "ck_alpha_invitations_athlete_invitation_has_athlete",
        "alpha_invitations",
        type_="check",
    )


def downgrade():
    op.create_check_constraint(
        "ck_alpha_invitations_athlete_invitation_has_athlete",
        "alpha_invitations",
        "role <> 'athlete' OR athlete_id IS NOT NULL",
    )
