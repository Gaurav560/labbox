"""Lesson progress: current step per chapter, hints used and first pass per task.

Revision ID: 0002
Revises: 0001
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chapter_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lab_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chapter_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("current_step", sa.Integer(), nullable=False),
        sa.Column("setup_done", sa.Boolean(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("user_id", "lab_id", "chapter_id"),
    )
    op.create_table(
        "task_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lab_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("task_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chapter_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("hints_used", sa.Integer(), nullable=False),
        sa.Column("first_passed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("user_id", "lab_id", "task_id"),
    )


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
