"""Before you start (owner, 24 November: "add prerequisites for every lab, in detail")."""
import random
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.labs import all_labs


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def test_every_lab_says_what_it_needs():
    ids = {lab.id for lab in all_labs()}
    for lab in all_labs():
        assert lab.before_you_start is not None, lab.id
        assert lab.before_you_start.summary.strip(), lab.id
        for need in lab.before_you_start.needs:
            assert need.know.strip(), lab.id
            assert need.lab is None or (need.lab in ids and need.lab != lab.id), (lab.id, need.lab)


def test_the_course_page_gets_it_with_lab_titles(api):
    r = api.post("/api/auth/signup", json={"username": f"before{random.randint(0, 10**8)}", "password": "secret123"})
    headers = {"Authorization": f"Bearer {r.json()['token']}"}
    box = api.get("/api/labs/rag-vector-databases", headers=headers).json()["before_you_start"]
    assert box["summary"]
    python = next(n for n in box["needs"] if n["lab"] == "python-basics")
    assert python["lab_title"] == "Python from zero" and python["where"]
    plain = api.get("/api/labs/python-basics", headers=headers).json()["before_you_start"]
    assert plain["needs"] == [] and plain["summary"].startswith("Nothing.")
