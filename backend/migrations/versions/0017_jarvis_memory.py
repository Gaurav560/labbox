"""Jarvis remembers (owner, 28 November, step 3): jarvis_session.summary, the few sentences Jarvis keeps from a
conversation for the next ones. Additive only.

Revision ID: 0017
Revises: 0016
"""
import sqlalchemy as sa
from alembic import op

revision = "0017"
down_revision = "0016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("jarvis_session", schema=None) as batch_op:
        batch_op.add_column(sa.Column("summary", sa.String(), nullable=True))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
