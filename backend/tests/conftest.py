import os
import sys
import tempfile
from pathlib import Path

# Tests never use the developer's .env values: isolated secret, database and folders.
_TMP = Path(tempfile.mkdtemp(prefix="labbox-tests-"))
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-123"
os.environ["DATABASE_URL"] = f"sqlite:///{_TMP}/test.db"
os.environ["VOLUMES_DIR"] = str(_TMP / "volumes")
os.environ["CHECKS_DIR"] = str(_TMP / "checks")
os.environ["LABS_DIR"] = str(Path(__file__).resolve().parents[2] / "labs")
os.environ["ALLOW_SIGNUP"] = "true"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_sessionfinish(session, exitstatus):
    import shutil

    shutil.rmtree(_TMP, ignore_errors=True)
