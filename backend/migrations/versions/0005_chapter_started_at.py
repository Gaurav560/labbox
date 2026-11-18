"""chapter_progress.started_at: when the learner first opened the chapter on a running machine.

Revision ID: 0005
Revises: 0004
"""
import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("chapter_progress", schema=None) as batch_op:
        batch_op.add_column(sa.Column("started_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
