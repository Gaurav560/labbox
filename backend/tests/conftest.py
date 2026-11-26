import os
import sys
import tempfile
from pathlib import Path

# Tests never use the developer's .env values: isolated secret, database and folders.
_TMP = Path(tempfile.mkdtemp(prefix="labbox-tests-"))
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-123"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
# The same tests on Postgres: LABBOX_TEST_DATABASE_URL=postgresql+psycopg://.../labbox_test pytest
# (only a database whose name ends in _test, and it is emptied first).
_PG = os.environ.get("LABBOX_TEST_DATABASE_URL")
if _PG:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import make_url

    if not (make_url(_PG).database or "").endswith("_test"):
        raise SystemExit("LABBOX_TEST_DATABASE_URL must name a database ending in _test (it is emptied).")
    _e = create_engine(_PG)
    with _e.begin() as c:
        c.execute(text("DROP SCHEMA public CASCADE"))
        c.execute(text("CREATE SCHEMA public"))
    _e.dispose()
    os.environ["DATABASE_URL"] = _PG
# Shared state in memory unless LABBOX_TEST_REDIS_URL=redis://.../15 (a Redis database other than 0,
# never the app's own; it is emptied first).
os.environ["REDIS_URL"] = ""
_RD = os.environ.get("LABBOX_TEST_REDIS_URL")
if _RD:
    import redis

    _r = redis.Redis.from_url(_RD)
    if int(_r.connection_pool.connection_kwargs.get("db", 0)) == 0:
        raise SystemExit("LABBOX_TEST_REDIS_URL must name a Redis database other than 0 (it is emptied), e.g. /15.")
    _r.flushdb()
    _r.close()
    os.environ["REDIS_URL"] = _RD
os.environ["VOLUMES_DIR"] = str(_TMP / "volumes")
os.environ["CHECKS_DIR"] = str(_TMP / "checks")
os.environ["LIBRARY_UPLOADS_DIR"] = str(_TMP / "library")
os.environ["BACKUP_DIR"] = str(_TMP / "backups")  # never the real backups (rotation deletes old ones)
os.environ["LABS_DIR"] = str(Path(__file__).resolve().parents[2] / "labs")
os.environ["ALLOW_SIGNUP"] = "true"
# Tests are the unnamed (development) instance, never the live site's (INSTANCE=prod in its own .env).
os.environ["INSTANCE"] = ""
os.environ["RELEASE"] = ""
os.environ["PUBLIC_URL"] = ""
# The gateway is tested in-process with the fake provider; no second server, no real models.
os.environ["LLM_GATEWAY_ENABLED"] = "false"
# VS Code in labs is tested on purpose (test_ide_docker.py); other tests keep the classic setup.
os.environ["IDE_ENABLED"] = "false"
os.environ["LLM_MODELS"] = "lab-chat=fake/chat-small,lab-chat-smart=fake/chat-big,lab-embed=fake/embed,lab-code=fake/code,ai-chat=fake/chat-small,ai-embed=fake/embed"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _test_ids_start_high() -> None:
    """Test accounts get 8-digit ids, so their machines (lab-u<id>-<lab>) can never share a name with a
    real account's machine on this computer (lab-u1-... is the owner's), and the Docker tests' cleanup
    (names lab-u<8 digits>-) removes them all. Postgres ids come from a sequence that ignores ids
    inserted by hand, so the sequence itself is moved; SQLite continues after the highest id."""
    import random

    from sqlalchemy import text
    from sqlmodel import Session

    from app.db import engine, init_db
    from app.models import User

    init_db()
    start = random.randint(10_000_000, 89_000_000)
    with Session(engine) as s:
        if engine.dialect.name == "postgresql":
            s.exec(text(f"SELECT setval(pg_get_serial_sequence('\"user\"', 'id'), {start})"))
        else:
            s.add(User(id=start, username=f"ids-start-here-{start}", password_hash="x"))
        s.commit()


_test_ids_start_high()


def pytest_sessionfinish(session, exitstatus):
    import shutil

    shutil.rmtree(_TMP, ignore_errors=True)
