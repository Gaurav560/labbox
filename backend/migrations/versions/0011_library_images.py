"""The Library shows real pictures (owner, 24 November): book covers, the first page of each paper, a view of each
blog. Adds library_item.image and fills it for the starting list from library/seed.yaml, matching by title; also
brings in a blog added to the starting list (The GitHub Blog) when the database has the one it replaced.

Revision ID: 0011
Revises: 0010
"""
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

SEED = Path(__file__).resolve().parents[3] / "library" / "seed.yaml"


def upgrade() -> None:
    with op.batch_alter_table("library_item", schema=None) as batch_op:
        batch_op.add_column(sa.Column("image", sa.String(), nullable=False, server_default=""))
    if not SEED.exists():
        return
    data = yaml.safe_load(SEED.read_text()) or {}
    table = sa.table("library_item", sa.column("id", sa.Integer), sa.column("title", sa.String),
                     sa.column("image", sa.String), sa.column("kind", sa.String), sa.column("authors", sa.String),
                     sa.column("year", sa.Integer), sa.column("url", sa.String), sa.column("note", sa.String),
                     sa.column("topic", sa.String), sa.column("lab", sa.String), sa.column("practice", sa.String),
                     sa.column("level", sa.String), sa.column("free", sa.Boolean), sa.column("featured", sa.Boolean),
                     sa.column("position", sa.Integer), sa.column("created_at", sa.DateTime),
                     sa.column("updated_at", sa.DateTime))
    bind = op.get_bind()
    # Netflix's blog blocks automated visits, so no real picture of it can be made: the starting list replaced it with
    # The GitHub Blog. Swap it in place (same position) in databases that still have the untouched seeded row.
    old = bind.execute(sa.select(table.c.id).where(table.c.title == "Netflix TechBlog",
                                                   table.c.url == "https://netflixtechblog.com/")).first()
    if old is not None:
        new = next((b for b in data.get("blogs") or [] if b["title"].startswith("The GitHub Blog")), None)
        if new:
            bind.execute(table.update().where(table.c.id == old.id).values(
                title=new["title"], authors=new.get("authors", ""), url=new["url"], topic=new.get("topic", ""),
                note=" ".join(str(new.get("note", "")).split()), lab=new.get("lab", ""), practice=new.get("practice", ""),
                free=bool(new.get("free", False)), updated_at=datetime.now(timezone.utc).replace(tzinfo=None)))
    for group in ("books", "papers", "blogs"):
        for item in data.get(group) or []:
            if item.get("image"):
                op.execute(table.update().where(table.c.title == str(item["title"])).values(image=str(item["image"])))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
