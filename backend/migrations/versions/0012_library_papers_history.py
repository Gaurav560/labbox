"""Premium Reads: the history of language models as the first papers (owner, 25 November). Adds three papers from
library/seed.yaml to databases that do not have them yet (GPT-1, Scaling Laws, InstructGPT; matched by link), then
orders the papers as the seed lists them: Attention Is All You Need, word2vec, GPT-1, BERT, Scaling Laws, GPT-3,
InstructGPT, Chain-of-Thought, then the rest. Papers an admin added keep their order, after the seeded ones.
Additive: no row is removed or rewritten except its position.

Revision ID: 0012
Revises: 0011
"""
from datetime import datetime, timezone
from pathlib import Path

import sqlalchemy as sa
import yaml
from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None

SEED = Path(__file__).resolve().parents[3] / "library" / "seed.yaml"
NEW = ("Improving Language Understanding by Generative Pre-Training", "Scaling Laws for Neural Language Models",
       "Training language models to follow instructions with human feedback")


def upgrade() -> None:
    if not SEED.exists():
        return
    papers = (yaml.safe_load(SEED.read_text()) or {}).get("papers") or []
    table = sa.table("library_item", sa.column("id", sa.Integer), sa.column("kind", sa.String),
                     sa.column("title", sa.String), sa.column("authors", sa.String), sa.column("year", sa.Integer),
                     sa.column("url", sa.String), sa.column("note", sa.String), sa.column("topic", sa.String),
                     sa.column("lab", sa.String), sa.column("practice", sa.String), sa.column("level", sa.String),
                     sa.column("free", sa.Boolean), sa.column("featured", sa.Boolean), sa.column("image", sa.String),
                     sa.column("position", sa.Integer), sa.column("created_at", sa.DateTime),
                     sa.column("updated_at", sa.DateTime))
    bind = op.get_bind()
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    have = {row.url for row in bind.execute(sa.select(table.c.url).where(table.c.kind == "paper"))}
    for item in papers:
        if str(item["title"]) in NEW and item["url"] not in have:
            bind.execute(table.insert().values(
                kind="paper", title=str(item["title"]), authors=str(item.get("authors", "")), year=item.get("year"),
                url=item["url"], note=" ".join(str(item.get("note", "")).split()), topic=item.get("topic", ""),
                lab=item.get("lab", ""), practice=item.get("practice", ""), level=item.get("level", ""),
                free=bool(item.get("free", False)), featured=False, image=item.get("image", ""), position=0,
                created_at=now, updated_at=now))
    seed_order = {str(item["title"]): i for i, item in enumerate(papers)}
    rows = bind.execute(sa.select(table.c.id, table.c.title, table.c.position).where(table.c.kind == "paper")
                        .order_by(table.c.position, table.c.id)).all()
    extra = len(seed_order)
    for row in rows:
        position = seed_order.get(row.title)
        if position is None:
            position, extra = extra, extra + 1
        bind.execute(table.update().where(table.c.id == row.id).values(position=position))


def downgrade() -> None:
    raise NotImplementedError("Migrations are additive only; restore a backup instead of downgrading")
