"""Jarvis, the learner's realtime voice assistant (owner, 28 November): user.plan ("free" or "pro") and jarvis_session
(one row per voice conversation, with its length and measured cost). Additive only.

Revision ID: 0016
Revises: 0015
"""
import sqlalchemy as sa
from alembic import op

revision = "0016"
down_revision = "0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("plan", sa.String(), nullable=False, server_default="free"))
    op.create_table(
        "jarvis_session",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("lab_id", sa.String(), nullable=True),
        sa.Column("chapter_id", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("seconds", sa.Integer(), nullable=False),
        sa.Column("max_seconds", sa.Integer(), nullable=False),
        sa.Column("audio_in_tokens", sa.Integer(), nullable=False),
        sa.Column("audio_cached_tokens", sa.Integer(), nullable=False),
        sa.Column("text_in_tokens", sa.Integer(), nullable=False),
        sa.Column("text_cached_tokens", sa.Integer(), nullable=False),
        sa.Column("audio_out_tokens", sa.Integer(), nullable=False),
        sa.Column("text_out_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_usd", sa.Float(), nullable=False),
        sa.Column("call_id", sa.String(), nullable=True),
    )
    op.create_index("ix_jarvis_session_user_id", "jarvis_session", ["user_id"])
    op.create_index("ix_jarvis_session_started_at", "jarvis_session", ["started_at"])


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
