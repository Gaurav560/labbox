"""Every check runs inside the chapter's folder, with the learner's modules importable and a fake model server."""
import os
import sys

import pytest

sys.path.insert(0, os.getcwd())
from fake_openai import FakeOpenAI  # noqa: E402

FAKE = FakeOpenAI()
os.environ["OPENAI_BASE_URL"] = FAKE.base_url
os.environ["OPENAI_API_KEY"] = "check-key"


@pytest.fixture
def fake():
    FAKE.reset()
    return FAKE
