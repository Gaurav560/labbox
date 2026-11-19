"""design_answer: graded attempts at design steps (Phase G).

Revision ID: 0007
Revises: 0006
"""
import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "design_answer",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("lab_id", sa.String(), nullable=False),
        sa.Column("chapter_id", sa.String(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("answers_json", sa.String(), nullable=False),
        sa.Column("result_json", sa.String(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_design_answer_user_id", "design_answer", ["user_id"])


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
