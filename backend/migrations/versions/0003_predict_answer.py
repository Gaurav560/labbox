"""Predict answers: every attempt at a predict step.

Revision ID: 0003
Revises: 0002
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "predict_answer",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lab_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chapter_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("step_index", sa.Integer(), nullable=False),
        sa.Column("choice", sa.Integer(), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("predict_answer", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_predict_answer_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
