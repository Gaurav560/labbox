"""Jarvis settings (owner, 28 November, step 4): user.jarvis_mode ("tap", "first" or "off") and user.jarvis_note_seen
(the note on what Jarvis can see was read). Additive only.

Revision ID: 0018
Revises: 0017
"""
import sqlalchemy as sa
from alembic import op

revision = "0018"
down_revision = "0017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("jarvis_mode", sa.String(), nullable=False, server_default="tap"))
        batch_op.add_column(sa.Column("jarvis_note_seen", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
