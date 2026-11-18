"""Alembic environment. Rule: migrations only ever add (tables, nullable or defaulted columns)."""
from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel

from app import models  # noqa: F401  (registers tables)
from app.db import engine

config = context.config
# Only the CLI sets up logging here; when the app runs migrations it keeps its own logging.
if config.config_file_name is not None and not config.attributes.get("from_app"):
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    context.configure(url=str(engine.url), target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def _run(connection) -> None:
    # render_as_batch: SQLite cannot ALTER most things in place.
    context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connection = config.attributes.get("connection")  # passed in by app.db.init_db
    if connection is not None:
        _run(connection)
        return
    with engine.connect() as connection:
        _run(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
