"""Phase H1: copying the database to a new one (SQLite to Postgres), with the source left untouched."""
import hashlib
import os
from datetime import date

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlmodel import Session, select

from app.db import init_db
from app.dbcopy import CopyError, copy_database, open_source
from app.models import ChapterProgress, User, Workspace, XpEvent


def _source(path) -> str:
    url = f"sqlite:///{path}"
    e = create_engine(url)
    init_db(e)
    with Session(e) as s:
        for i in (1, 2, 7):  # a gap in the ids, as after a deleted account
            s.add(User(id=i, username=f"learner{i}", password_hash="x"))
        s.commit()
        s.add(Workspace(user_id=7, lab_id="go-basics", container_name="lab-u7-go-basics", volume_path="/v", seeded=True))
        s.add(ChapterProgress(user_id=7, lab_id="go-basics", chapter_id="01", setup_done=True))
        s.add(XpEvent(user_id=7, kind="task", ref="task:go-basics:total", amount=20, day=date(2026, 11, 19)))
        s.commit()
    e.dispose()
    return url


def _digest(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_copy_keeps_every_row_and_leaves_the_source_alone(tmp_path):
    src = _source(tmp_path / "old.db")
    before = _digest(tmp_path / "old.db")
    target = create_engine(f"sqlite:///{tmp_path / 'new.db'}")
    counts = copy_database(open_source(src), target)
    assert all(c.ok for c in counts)
    assert {c.table: c.target for c in counts}["user"] == 3
    with Session(target) as s:
        assert [u.id for u in s.exec(select(User).order_by(User.id))] == [1, 2, 7]
        ws = s.exec(select(Workspace)).one()
        assert ws.seeded is True and ws.created_at is not None
    assert _digest(tmp_path / "old.db") == before  # read-only: not one byte changed


def test_copy_refuses_a_target_that_has_data(tmp_path):
    src = _source(tmp_path / "old.db")
    busy = _source(tmp_path / "busy.db")
    with pytest.raises(CopyError, match="already has rows"):
        copy_database(open_source(src), create_engine(busy))


def test_copy_refuses_an_old_or_empty_source(tmp_path):
    create_engine(f"sqlite:///{tmp_path / 'empty.db'}").connect().close()
    with pytest.raises(CopyError, match="revision"):
        copy_database(open_source(f"sqlite:///{tmp_path / 'empty.db'}"), create_engine(f"sqlite:///{tmp_path / 'n.db'}"))


@pytest.mark.skipif(not os.environ.get("LABBOX_TEST_DATABASE_URL"), reason="needs a Postgres test server")
def test_copy_to_postgres_continues_ids_after_the_highest(tmp_path):
    admin = make_url(os.environ["LABBOX_TEST_DATABASE_URL"])
    name = "labbox_copy_test"
    a = create_engine(admin, isolation_level="AUTOCOMMIT")
    with a.connect() as c:
        c.execute(text(f"DROP DATABASE IF EXISTS {name}"))
        c.execute(text(f"CREATE DATABASE {name}"))
    target = create_engine(admin.set(database=name))
    try:
        counts = copy_database(open_source(_source(tmp_path / "old.db")), target)
        assert all(c.ok for c in counts)
        with Session(target) as s:
            new = User(username="after-the-move", password_hash="x")
            s.add(new)
            s.commit()
            assert new.id == 8  # not 1: that id already belongs to someone
    finally:
        target.dispose()
        with a.connect() as c:
            c.execute(text(f"DROP DATABASE IF EXISTS {name}"))
        a.dispose()
