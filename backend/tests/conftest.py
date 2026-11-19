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
# The gateway is tested in-process with the fake provider; no second server, no real models.
os.environ["LLM_GATEWAY_ENABLED"] = "false"
# VS Code in labs is tested on purpose (test_ide_docker.py); other tests keep the classic setup.
os.environ["IDE_ENABLED"] = "false"
os.environ["LLM_MODELS"] = "lab-chat=fake/chat-small,lab-chat-smart=fake/chat-big,lab-embed=fake/embed,lab-code=fake/code"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def pytest_sessionfinish(session, exitstatus):
    import shutil

    shutil.rmtree(_TMP, ignore_errors=True)
