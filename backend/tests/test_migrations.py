"""Alembic migrations: fresh databases, POC databases (no alembic_version), and model drift."""
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlmodel import SQLModel

from app import models  # noqa: F401
from app.db import init_db

NEW_TABLES = {"chapter_progress", "task_progress", "predict_answer", "user_profile", "xp_event", "drill_answer", "llm_request", "design_answer"}
HEAD = "0007"

# The schema exactly as the POC's SQLModel.metadata.create_all() made it.
POC_SCHEMA = """
CREATE TABLE user (id INTEGER NOT NULL, username VARCHAR NOT NULL, password_hash VARCHAR NOT NULL,
    created_at DATETIME NOT NULL, PRIMARY KEY (id));
CREATE UNIQUE INDEX ix_user_username ON user (username);
CREATE TABLE workspace (id INTEGER NOT NULL, user_id INTEGER NOT NULL, lab_id VARCHAR NOT NULL,
    container_name VARCHAR NOT NULL, volume_path VARCHAR NOT NULL, seeded BOOLEAN NOT NULL,
    last_active_at DATETIME NOT NULL, created_at DATETIME NOT NULL, PRIMARY KEY (id),
    UNIQUE (user_id, lab_id), FOREIGN KEY(user_id) REFERENCES user (id), UNIQUE (container_name));
CREATE INDEX ix_workspace_lab_id ON workspace (lab_id);
CREATE INDEX ix_workspace_user_id ON workspace (user_id);
CREATE TABLE checkrun (id INTEGER NOT NULL, user_id INTEGER NOT NULL, lab_id VARCHAR NOT NULL,
    chapter_id VARCHAR NOT NULL, passed_count INTEGER NOT NULL, total_count INTEGER NOT NULL,
    results_json VARCHAR NOT NULL, output_tail VARCHAR NOT NULL, duration_ms INTEGER NOT NULL,
    created_at DATETIME NOT NULL, PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES user (id));
CREATE INDEX ix_checkrun_lab_id ON checkrun (lab_id);
CREATE INDEX ix_checkrun_user_id ON checkrun (user_id);
"""


def _engine(path: Path):
    return create_engine(f"sqlite:///{path}")


def _version(engine) -> str:
    with engine.connect() as c:
        return c.execute(text("SELECT version_num FROM alembic_version")).scalar_one()


def test_fresh_database(tmp_path: Path):
    engine = _engine(tmp_path / "fresh.db")
    init_db(engine)
    assert {"user", "workspace", "checkrun", *NEW_TABLES} <= set(inspect(engine).get_table_names())
    assert _version(engine) == HEAD
    init_db(engine)  # running again is a no-op
    assert _version(engine) == HEAD


def test_poc_database_is_stamped_and_keeps_data(tmp_path: Path):
    engine = _engine(tmp_path / "poc.db")
    with engine.begin() as c:
        for stmt in POC_SCHEMA.split(";"):
            if stmt.strip():
                c.execute(text(stmt))
        c.execute(text("INSERT INTO user (id, username, password_hash, created_at) VALUES (1, 'asha', 'x', '2026-01-01')"))
        c.execute(
            text(
                "INSERT INTO checkrun (user_id, lab_id, chapter_id, passed_count, total_count, results_json,"
                " output_tail, duration_ms, created_at) VALUES (1, 'python-basics', '01-functions', 1, 3, '[]', '', 5, '2026-01-01')"
            )
        )
    init_db(engine)
    assert _version(engine) == HEAD
    assert NEW_TABLES <= set(inspect(engine).get_table_names())
    with engine.connect() as c:
        assert c.execute(text("SELECT username FROM user")).scalar_one() == "asha"
        assert c.execute(text("SELECT count(*) FROM checkrun")).scalar_one() == 1
        # Existing users get a profile: onboarded already, earlier progress not yet turned into XP.
        row = c.execute(text("SELECT user_id, onboarded_at, backfilled_at FROM user_profile")).one()
        assert row[0] == 1 and row[1] is not None and row[2] is None


def test_models_match_migrations(tmp_path: Path):
    """Fails when a model changes without a migration (write one with alembic revision --autogenerate)."""
    engine = _engine(tmp_path / "drift.db")
    init_db(engine)
    with engine.connect() as c:
        diff = compare_metadata(MigrationContext.configure(c), SQLModel.metadata)
    assert diff == []
