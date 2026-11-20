"""Admin role and analytics events (Phase J).

Revision ID: 0008
Revises: 0007
"""
import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_table(
        "analytics_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("lab_id", sa.String(), nullable=True),
        sa.Column("chapter_id", sa.String(), nullable=True),
        sa.Column("step_index", sa.Integer(), nullable=True),
        sa.Column("data_json", sa.String(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_analytics_event_user_id", "analytics_event", ["user_id"])
    op.create_index("ix_analytics_event_kind", "analytics_event", ["kind"])
    op.create_index("ix_analytics_event_lab_id", "analytics_event", ["lab_id"])
    op.create_index("ix_analytics_event_created_at", "analytics_event", ["created_at"])


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
