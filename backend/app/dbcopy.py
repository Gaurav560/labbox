"""Copy a LabBox database to a new, empty one (Phase H1: SQLite to Postgres), table by table.

The source is only read (SQLite is opened read-only), and is never changed or deleted. The target gets
the schema from the Alembic migrations first, so both end on the same revision. Rows keep their ids;
Postgres id sequences then continue after the highest copied id. Row counts are compared at the end.

    scripts/labbox db-copy --to postgresql+psycopg://...   (from backend/data/labbox.db by default)
"""
from dataclasses import dataclass

from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, func, inspect, select, text
from sqlalchemy.engine import make_url
from sqlmodel import SQLModel

from . import models  # noqa: F401  (registers every table on SQLModel.metadata)
from .db import alembic_config, init_db

BATCH = 1000
# Tables the migrations fill with starting data (the Library's first reading list). A fresh target already has those
# rows; the source has its own (perhaps edited by admins), so they are replaced instead of counting as "not empty".
SEEDED = {"library_item"}


class CopyError(Exception):
    pass


@dataclass
class TableCount:
    table: str
    source: int
    target: int

    @property
    def ok(self) -> bool:
        return self.source == self.target


def open_source(url: str) -> Engine:
    """SQLite read-only (the file cannot be changed by mistake); anything else as given."""
    u = make_url(url)
    if u.get_backend_name() == "sqlite" and u.database:
        return create_engine(f"sqlite:///file:{u.database}?mode=ro&uri=true")
    return create_engine(url)


def head_revision() -> str:
    return ScriptDirectory.from_config(alembic_config()).get_current_head()


def revision(engine: Engine) -> str | None:
    if "alembic_version" not in inspect(engine).get_table_names():
        return None
    with engine.connect() as c:
        return c.execute(text("SELECT version_num FROM alembic_version")).scalar()


def count(engine: Engine, table) -> int:
    with engine.connect() as c:
        return c.execute(select(func.count()).select_from(table)).scalar_one()


def copy_database(source: Engine, target: Engine) -> list[TableCount]:
    head = head_revision()
    if revision(source) != head:
        raise CopyError(f"The source is at revision {revision(source)}, not {head}. Start the backend on it once "
                        "(it upgrades itself), then copy.")
    init_db(target)  # schema from the migrations, the same as a fresh install
    tables = SQLModel.metadata.sorted_tables  # parents before children (foreign keys)
    full = [t.name for t in tables if t.name not in SEEDED and count(target, t)]
    if full:
        raise CopyError(f"The target already has rows in: {', '.join(full)}. Copy only into an empty database.")

    with source.connect() as src, target.begin() as dst:
        for t in tables:
            if t.name in SEEDED:
                dst.execute(t.delete())
        for t in tables:
            rows = src.execute(select(t)).mappings()
            while batch := [dict(r) for r in rows.fetchmany(BATCH)]:
                dst.execute(t.insert(), batch)
        if target.dialect.name == "postgresql":
            # Ids were copied as they are, so each id sequence must continue after the highest one.
            for t in tables:
                pk = list(t.primary_key.columns)
                if len(pk) == 1 and pk[0].autoincrement in (True, "auto") and pk[0].type.python_type is int:
                    dst.execute(text(
                        f"SELECT setval(pg_get_serial_sequence('\"{t.name}\"', '{pk[0].name}'), "
                        f"COALESCE(MAX(\"{pk[0].name}\"), 1), MAX(\"{pk[0].name}\") IS NOT NULL) FROM \"{t.name}\""
                    ))
    return [TableCount(t.name, count(source, t), count(target, t)) for t in tables]
