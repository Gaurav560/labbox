"""Alembic migrations: fresh databases, POC databases (no alembic_version), and model drift."""
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect, text
from sqlmodel import SQLModel

from app import models  # noqa: F401
from alembic import command

from app.db import alembic_config, init_db

NEW_TABLES = {"chapter_progress", "task_progress", "predict_answer", "user_profile", "xp_event", "drill_answer", "llm_request", "design_answer", "analytics_event", "library_item", "site_setting", "lab_slot", "certificate", "user_identity"}
HEAD = "0016"

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


def test_library_papers_reach_an_existing_database(tmp_path: Path):
    """Migration 0012 (owner, 25 November): a database seeded before the three history papers gets them, and the
    papers come in the seed's order (Attention, word2vec, GPT-1, BERT, Scaling Laws, GPT-3, InstructGPT, CoT)."""
    engine = _engine(tmp_path / "old.db")
    cfg = alembic_config()
    with engine.begin() as connection:
        cfg.attributes["connection"] = connection
        command.upgrade(cfg, "0011")
        # an older seed: no GPT-1, Scaling Laws or InstructGPT, and Attention not first
        connection.execute(text("DELETE FROM library_item WHERE title IN ('Improving Language Understanding by Generative"
                                " Pre-Training', 'Scaling Laws for Neural Language Models', 'Training language models"
                                " to follow instructions with human feedback')"))
        connection.execute(text("UPDATE library_item SET position = 99 WHERE title = 'Attention Is All You Need'"))
        connection.execute(text("INSERT INTO library_item (kind, title, authors, url, note, topic, lab, practice, level,"
                                " free, featured, image, position, created_at, updated_at) VALUES ('paper', 'Added by"
                                " an admin', '', 'https://example.com/x', '', '', '', '', '', 0, 0, '', 3,"
                                " '2026-11-01', '2026-11-01')"))
    init_db(engine)
    assert _version(engine) == HEAD
    with engine.connect() as c:
        titles = [r[0] for r in c.execute(text("SELECT title FROM library_item WHERE kind = 'paper' ORDER BY position, id"))]
    assert titles[:8] == ["Attention Is All You Need", "Efficient Estimation of Word Representations in Vector Space",
                          "Improving Language Understanding by Generative Pre-Training",
                          "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                          "Scaling Laws for Neural Language Models", "Language Models are Few-Shot Learners",
                          "Training language models to follow instructions with human feedback",
                          "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"]
    assert titles[-1] == "Added by an admin" and titles.count("Scaling Laws for Neural Language Models") == 1
