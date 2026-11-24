"""The Library, redesigned as a public page (owner, 24 November): each item can name the lab where you practise it,
a level, whether it is free to read, and whether it is its section's "Start here" pick. Fills the new columns for the
starting list from library/seed.yaml, matching by title.

Revision ID: 0010
Revises: 0009
"""
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

SEED = Path(__file__).resolve().parents[3] / "library" / "seed.yaml"


def upgrade() -> None:
    with op.batch_alter_table("library_item", schema=None) as batch_op:
        batch_op.add_column(sa.Column("lab", sa.String(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("practice", sa.String(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("level", sa.String(), nullable=False, server_default=""))
        batch_op.add_column(sa.Column("free", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("featured", sa.Boolean(), nullable=False, server_default=sa.false()))
    if not SEED.exists():
        return
    data = yaml.safe_load(SEED.read_text()) or {}
    table = sa.table("library_item", sa.column("title", sa.String), sa.column("lab", sa.String),
                     sa.column("practice", sa.String), sa.column("level", sa.String), sa.column("free", sa.Boolean),
                     sa.column("featured", sa.Boolean))
    for group in ("books", "papers", "blogs"):
        for item in data.get(group) or []:
            op.execute(table.update().where(table.c.title == str(item["title"])).values(
                lab=str(item.get("lab", "")), practice=str(item.get("practice", "")), level=str(item.get("level", "")),
                free=bool(item.get("free", False)), featured=bool(item.get("featured", False))))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
