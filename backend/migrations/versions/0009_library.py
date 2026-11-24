"""The Library: books, research papers and tech blogs (owner, 24 November). Creates library_item and fills it
once from library/seed.yaml; admins change the list in the app after that.

Revision ID: 0009
Revises: 0008
"""
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

SEED = Path(__file__).resolve().parents[3] / "library" / "seed.yaml"
KINDS = {"books": "book", "papers": "paper", "blogs": "blog"}


def upgrade() -> None:
    table = op.create_table(
        "library_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.String(), nullable=False, server_default=""),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("url", sa.String(), nullable=False, server_default=""),
        sa.Column("note", sa.String(), nullable=False, server_default=""),
        sa.Column("topic", sa.String(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_library_item_kind", "library_item", ["kind"])
    if not SEED.exists():
        return
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    data = yaml.safe_load(SEED.read_text()) or {}
    rows = []
    for group, kind in KINDS.items():
        for position, item in enumerate(data.get(group) or []):
            rows.append({"kind": kind, "title": str(item["title"]), "authors": str(item.get("authors", "")),
                         "year": item.get("year"), "url": str(item.get("url", "")),
                         "note": " ".join(str(item.get("note", "")).split()), "topic": str(item.get("topic", "")),
                         "position": position, "created_at": now, "updated_at": now})
    if rows:
        op.bulk_insert(table, rows)


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
