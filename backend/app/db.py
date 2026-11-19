import logging
from collections.abc import Iterator
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect
from sqlmodel import Session, create_engine

from .config import BACKEND_DIR, get_settings

log = logging.getLogger(__name__)

# The last revision whose tables the POC created with SQLModel.metadata.create_all().
POC_BASELINE = "0001"

_url = get_settings().DATABASE_URL
if _url.startswith("sqlite:///"):
    Path(_url.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

if _url.startswith("sqlite"):
    engine = create_engine(_url, connect_args={"check_same_thread": False})
else:
    # Postgres (Phase H1): a small pool per worker; pre_ping replaces connections the server dropped
    # (a database restart), so a request never fails on a stale one.
    engine = create_engine(_url, pool_size=10, max_overflow=20, pool_pre_ping=True, pool_recycle=1800)


def alembic_config() -> Config:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.attributes["from_app"] = True
    return cfg


def init_db(bind: Engine | None = None) -> None:
    """Bring the database schema up to date with Alembic migrations (additive only)."""
    bind = bind or engine
    cfg = alembic_config()
    with bind.begin() as connection:
        cfg.attributes["connection"] = connection
        tables = set(inspect(connection).get_table_names())
        if "alembic_version" not in tables and "user" in tables:
            # A POC database: its tables already exist, so record them instead of creating them again.
            log.info("Existing POC database found, stamping it at revision %s", POC_BASELINE)
            command.stamp(cfg, POC_BASELINE)
        command.upgrade(cfg, "head")


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
