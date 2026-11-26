"""At most a few labs at a time (owner, 26 November): lab_slot (the labs a learner unlocked), site_setting (the
admin's limit for everyone) and user.lab_limit (an admin's limit for one learner). Additive only.

Revision ID: 0013
Revises: 0012
"""
import sqlalchemy as sa
from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("lab_limit", sa.Integer(), nullable=True))
    op.create_table(
        "site_setting",
        sa.Column("key", sa.String(), primary_key=True),
        sa.Column("value", sa.String(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("updated_by", sa.Integer(), nullable=True),
    )
    op.create_table(
        "lab_slot",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), primary_key=True),
        sa.Column("lab_id", sa.String(), primary_key=True),
        sa.Column("unlocked_at", sa.DateTime(), nullable=False),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("released_reason", sa.String(), nullable=True),
    )


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
