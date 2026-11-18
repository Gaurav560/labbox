"""POC baseline: the tables that existed before v2 (user, workspace, checkrun).

Databases created by the POC (SQLModel create_all) are stamped at this revision on start-up.

Revision ID: 0001
Revises:
"""
import sqlalchemy as sa
import sqlmodel
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_username"), ["username"], unique=True)

    op.create_table(
        "checkrun",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lab_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("chapter_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("results_json", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("output_tail", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("checkrun", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_checkrun_lab_id"), ["lab_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_checkrun_user_id"), ["user_id"], unique=False)

    op.create_table(
        "workspace",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lab_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("container_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("volume_path", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("seeded", sa.Boolean(), nullable=False),
        sa.Column("last_active_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("container_name"),
        sa.UniqueConstraint("user_id", "lab_id"),
    )
    with op.batch_alter_table("workspace", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_workspace_lab_id"), ["lab_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_workspace_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
