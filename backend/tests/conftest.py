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
os.environ["VOLUMES_DIR"] = str(_TMP / "volumes")
os.environ["CHECKS_DIR"] = str(_TMP / "checks")
os.environ["LABS_DIR"] = str(Path(__file__).resolve().parents[2] / "labs")
os.environ["ALLOW_SIGNUP"] = "true"
# The gateway is tested in-process with the fake provider; no second server, no real models.
os.environ["LLM_GATEWAY_ENABLED"] = "false"
# VS Code in labs is tested on purpose (test_ide_docker.py); other tests keep the classic setup.
os.environ["IDE_ENABLED"] = "false"
os.environ["LLM_MODELS"] = "lab-chat=fake/chat-small,lab-chat-smart=fake/chat-big,lab-embed=fake/embed,lab-code=fake/code"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_sessionfinish(session, exitstatus):
    import shutil

    shutil.rmtree(_TMP, ignore_errors=True)
