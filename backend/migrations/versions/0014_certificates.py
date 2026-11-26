"""Certificates (owner, 27 November): certificate (one per learner and lab, public at /c/<id>) and
user_profile.certificate_name (the full name typed for the first certificate). Additive only.

Revision ID: 0014
Revises: 0013
"""
import sqlalchemy as sa
from alembic import op

revision = "0014"
down_revision = "0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_profile", schema=None) as batch_op:
        batch_op.add_column(sa.Column("certificate_name", sa.String(), nullable=True))
    op.create_table(
        "certificate",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("lab_id", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tasks_passed", sa.Integer(), nullable=False),
        sa.Column("tasks_total", sa.Integer(), nullable=False),
        sa.Column("chapters_total", sa.Integer(), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("name_corrected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("user_id", "lab_id"),
    )
    op.create_index("ix_certificate_user_id", "certificate", ["user_id"])


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
