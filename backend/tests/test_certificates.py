"""Certificates (owner, 27 November): earned at 80% of a lab's tasks, the full name typed once, a public page and a
share address with card tags for LinkedIn and X, a 1200 x 627 picture, hiding, and one name correction."""
import io
import math
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app import certificates, slots
from app.db import engine
from app.labs import get_lab
from app.models import TaskProgress, User, utcnow

from test_slots import pass_tasks, signup

LAB, OTHER = "python-basics", "python-collections"


@pytest.fixture(scope="module")
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app) as c:
        yield c


def tasks(lab_id: str) -> int:
    return sum(len(c.tasks) for c in get_lab(lab_id).chapters)


def needed(lab_id: str) -> int:
    return math.ceil(slots.FINISH_SHARE * tasks(lab_id))


def test_not_before_80_percent(api):
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB) - 1)
    st = api.get(f"/api/labs/{LAB}/certificate", headers=h).json()
    assert st["eligible"] is False and st["tasks_needed"] == needed(LAB) and st["certificate"] is None
    r = api.post(f"/api/labs/{LAB}/certificate", json={"name": "Asha Verma"}, headers=h)
    assert r.status_code == 409 and f"{needed(LAB)} of this lab's" in r.json()["detail"]


def test_claim_share_and_picture(api):
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB))
    assert api.get(f"/api/labs/{LAB}/certificate", headers=h).json()["eligible"] is True
    # The first certificate needs the name; a bad one is refused.
    assert api.post(f"/api/labs/{LAB}/certificate", json={}, headers=h).status_code == 422
    assert api.post(f"/api/labs/{LAB}/certificate", json={"name": "<b>x</b>"}, headers=h).status_code == 422
    cert = api.post(f"/api/labs/{LAB}/certificate", json={"name": "  Asha   Verma "}, headers=h).json()
    assert cert["name"] == "Asha Verma" and cert["lab_id"] == LAB and cert["mine"] is True
    assert len(cert["id"]) == 8 and set(cert["id"]) <= set(certificates.ID_ALPHABET)
    assert cert["tasks_passed"] == needed(LAB) and cert["tasks_total"] == tasks(LAB) and cert["skills"]
    # Claiming again returns the same certificate.
    assert api.post(f"/api/labs/{LAB}/certificate", json={}, headers=h).json()["id"] == cert["id"]

    # Public: the page data without a login, the share page with card tags, the picture.
    pub = api.get(f"/api/certificates/{cert['id']}").json()
    assert pub["name"] == "Asha Verma" and pub["mine"] is False
    page = api.get(f"/c/{cert['id']}", headers={"host": "labbox.example.org", "x-forwarded-proto": "https"})
    assert page.status_code == 200 and "text/html" in page.headers["content-type"]
    body = page.text
    assert 'property="og:title" content="Asha Verma completed' in body
    assert f'property="og:url" content="http://labbox.example.org/c/{cert["id"]}"' in body or "/c/" + cert["id"] in body
    assert 'name="twitter:card" content="summary_large_image"' in body
    assert f"/api/certificates/{cert['id']}/image.jpg" in body and f"/certificates/{cert['id']}" in body
    png = api.get(f"/api/certificates/{cert['id']}/image.jpg")
    assert png.status_code == 200 and png.headers["content-type"] == "image/jpeg"
    from PIL import Image

    assert Image.open(io.BytesIO(png.content)).size == (1200, 627)
    # Lower-case ids work too (people type them).
    assert api.get(f"/api/certificates/{cert['id'].lower()}").status_code == 200

    # Mine, listed.
    assert [c["id"] for c in api.get("/api/certificates", headers=h).json()] == [cert["id"]]


def test_names_are_escaped_and_missing_ones_404(api):
    assert api.get("/c/ZZZZZZZZ").status_code == 404
    assert api.get("/api/certificates/ZZZZZZZZ").status_code == 404
    assert api.get("/api/certificates/ZZZZZZZZ/image.jpg").status_code == 404
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB))
    cid = api.post(f"/api/labs/{LAB}/certificate", json={"name": "Ra'ees O'Neil-Dsouza"}, headers=h).json()["id"]
    body = api.get(f"/c/{cid}").text
    assert "Ra&#x27;ees O&#x27;Neil-Dsouza" in body and "Ra'ees O'Neil" not in body.split("<script>")[0]


def test_hide_and_one_correction(api):
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB))
    cid = api.post(f"/api/labs/{LAB}/certificate", json={"name": "Asha Varma"}, headers=h).json()["id"]
    fixed = api.patch(f"/api/certificates/{cid}", json={"name": "Asha Verma"}, headers=h).json()
    assert fixed["name"] == "Asha Verma" and fixed["name_corrected"] is True
    r = api.patch(f"/api/certificates/{cid}", json={"name": "Someone Else"}, headers=h)
    assert r.status_code == 409
    # Hidden: gone for everyone else, still there for its learner.
    assert api.patch(f"/api/certificates/{cid}", json={"hidden": True}, headers=h).json()["hidden"] is True
    assert api.get(f"/api/certificates/{cid}").status_code == 404
    assert api.get(f"/c/{cid}").status_code == 404
    assert api.get(f"/api/certificates/{cid}", headers=h).json()["mine"] is True
    # Someone else cannot change it.
    h2, _ = signup(api, "cert")
    assert api.patch(f"/api/certificates/{cid}", json={"hidden": False}, headers=h2).status_code == 404
    api.patch(f"/api/certificates/{cid}", json={"hidden": False}, headers=h)
    assert api.get(f"/api/certificates/{cid}").status_code == 200


def test_the_next_certificate_comes_by_itself(api):
    """After the first claim the name is known: the check that finishes another lab issues its certificate."""
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB))
    with Session(engine) as s:
        user = s.get(User, uid)
        # Finished, but no name yet: the check asks for it.
        assert certificates.after_check(s, user, get_lab(LAB)) == certificates.CheckCertificate(needs_name=True)
    api.post(f"/api/labs/{LAB}/certificate", json={"name": "Asha Verma"}, headers=h)
    pass_tasks(uid, OTHER, needed(OTHER) - 1)
    with Session(engine) as s:
        user = s.get(User, uid)
        assert certificates.after_check(s, user, get_lab(OTHER)) is None  # not finished yet
        assert certificates.after_check(s, user, get_lab(LAB)) is None  # has its certificate: no nagging
    lab = get_lab(OTHER)
    chapter, task = [(c.id, t.id) for c in lab.chapters for t in c.tasks][needed(OTHER) - 1]
    with Session(engine) as s:
        s.add(TaskProgress(user_id=uid, lab_id=OTHER, task_id=task, chapter_id=chapter, passed=True, first_passed_at=utcnow()))
        s.commit()
        user = s.get(User, uid)
        got = certificates.after_check(s, user, lab)
    assert got is not None and got.id
    other = api.get(f"/api/certificates/{got.id}").json()
    assert other["lab_id"] == OTHER and other["name"] == "Asha Verma"


def test_verify_from_the_server(api):
    """The QR code's page: what the server holds for an id (owner, 27 November: "verifies the authenticity from the
    backend"). Verified, private (hidden), unknown, the home page's sample, and the QR itself."""
    h, uid = signup(api, "cert")
    pass_tasks(uid, LAB, needed(LAB))
    cid = api.post(f"/api/labs/{LAB}/certificate", json={"name": "Asha Verma"}, headers=h).json()["id"]
    v = api.get(f"/api/verify/{cid.lower()}").json()
    assert v["status"] == "verified" and v["id"] == cid and v["name"] == "Asha Verma" and v["lab_id"] == LAB
    assert v["tasks_passed"] == needed(LAB) and v["issued_at"] and v["checked_at"]
    api.patch(f"/api/certificates/{cid}", json={"hidden": True}, headers=h)
    v = api.get(f"/api/verify/{cid}").json()
    assert v["status"] == "private" and v["name"] is None and v["lab_id"] is None
    assert api.get("/api/verify/ZZZZZZZZ").json()["status"] == "unknown"
    assert api.get("/api/verify/not-an-id!").json()["status"] == "unknown"
    assert api.get(f"/api/verify/{certificates.SAMPLE_ID}").json()["status"] == "sample"
    # The QR: an SVG for any well-formed id (it only holds the /verify address), 404 for anything else.
    qr = api.get(f"/api/certificates/{cid}/qr.svg")
    assert qr.status_code == 200 and qr.headers["content-type"].startswith("image/svg+xml") and b"<svg" in qr.content
    assert api.get("/api/certificates/bad/qr.svg").status_code == 404


def test_the_qr_holds_the_public_address(monkeypatch):
    """PUBLIC_URL wins over the request's address, so a picture made anywhere points at the real site."""
    from app.config import get_settings

    monkeypatch.setenv("PUBLIC_URL", "https://labbox.example.org/")
    get_settings.cache_clear()
    try:
        assert certificates.verify_url(certificates.public_base("http://localhost:8000"), "ABCDEFGH") == \
            "https://labbox.example.org/verify/ABCDEFGH"
    finally:
        monkeypatch.setenv("PUBLIC_URL", "")
        get_settings.cache_clear()
    assert certificates.public_base("http://localhost:8000") == "http://localhost:8000"
