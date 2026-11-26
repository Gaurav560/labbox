"""Sign in with Google and GitHub (owner, 27 November). The providers are faked (`oauth.fetch_identity`), so these run
with no network and no real accounts: the start, the state check, account matching and linking, invite-only sites,
the one-time code, and the buttons shown only when keys are set."""
import random
from collections.abc import Iterator
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import oauth
from app.config import get_settings
from app.db import engine
from app.models import User, UserIdentity


@pytest.fixture
def keys(monkeypatch) -> Iterator[None]:
    for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"):
        monkeypatch.setenv(k, f"test-{k.lower()}")
    get_settings.cache_clear()
    yield
    for k in ("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GITHUB_CLIENT_ID", "GITHUB_CLIENT_SECRET"):
        monkeypatch.setenv(k, "")
    monkeypatch.setenv("ALLOW_SIGNUP", "true")
    get_settings.cache_clear()


@pytest.fixture
def api() -> Iterator[TestClient]:
    from app.main import app

    with TestClient(app, follow_redirects=False) as c:
        yield c


def fake(monkeypatch, ident: oauth.Identity) -> None:
    monkeypatch.setattr(oauth, "fetch_identity", lambda provider, code, verifier, uri: ident)


def sign_in(api: TestClient, provider: str = "google", next_path: str | None = None) -> dict:
    """Start, come back from the provider, swap the code: the login answer (or the error redirect's query)."""
    start = api.get(f"/api/auth/oauth/{provider}/start", params={"next": next_path} if next_path else None)
    assert start.status_code == 302
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]
    back = api.get(f"/api/auth/oauth/{provider}/callback", params={"code": "c0de", "state": state})
    assert back.status_code == 302
    q = parse_qs(urlparse(back.headers["location"]).query)
    if "oauth_error" in q:
        return {"error": q["oauth_error"][0]}
    out = api.post("/api/auth/oauth/exchange", json={"code": q["oauth"][0]})
    assert out.status_code == 200, out.text
    return {**out.json(), "next": q["next"][0]}


def uid() -> str:
    return str(random.randint(10**9, 10**10))


def test_buttons_only_with_keys(api, keys, monkeypatch):
    assert api.get("/api/auth/options").json()["providers"] == ["google", "github"]
    monkeypatch.setenv("GITHUB_CLIENT_SECRET", "")
    get_settings.cache_clear()
    assert api.get("/api/auth/options").json()["providers"] == ["google"]
    assert api.get("/api/auth/oauth/github/start").status_code == 404


def test_start_sends_to_the_provider_with_state_and_pkce(api, keys):
    r = api.get("/api/auth/oauth/google/start", params={"next": "/courses/langchain"},
                headers={"x-forwarded-host": "labbox.example.org", "x-forwarded-proto": "https"})
    url = urlparse(r.headers["location"])
    q = parse_qs(url.query)
    assert url.netloc == "accounts.google.com" and q["client_id"] == ["test-google_client_id"]
    assert q["redirect_uri"] == ["https://labbox.example.org/api/auth/oauth/google/callback"]
    assert q["code_challenge_method"] == ["S256"] and q["scope"] == ["openid email profile"]
    assert "labbox_oauth" in r.headers["set-cookie"] and "HttpOnly" in r.headers["set-cookie"]
    g = urlparse(api.get("/api/auth/oauth/github/start").headers["location"])
    assert g.netloc == "github.com" and parse_qs(g.query)["scope"] == ["read:user user:email"]


def test_new_account_then_the_same_account_again(api, keys, monkeypatch):
    sub = uid()
    fake(monkeypatch, oauth.Identity("google", sub, f"meera.{sub}@example.org", "Meera Iyer", f"meera.{sub}"))
    first = sign_in(api, next_path="/courses/langchain")
    assert first["new"] is True and first["token"] and first["next"] == "/courses/langchain"
    assert first["user"]["username"] == f"meera.{sub}"
    again = sign_in(api)
    assert again["new"] is False and again["user"]["id"] == first["user"]["id"]
    with Session(engine) as s:
        u = s.get(User, first["user"]["id"])
        assert u.email == f"meera.{sub}@example.org" and u.email_verified_at is not None
    # The login works like a password login.
    me = api.get("/api/me", headers={"Authorization": f"Bearer {first['token']}"}).json()
    assert me["id"] == first["user"]["id"]


def test_github_with_the_same_verified_email_links_to_the_same_account(api, keys, monkeypatch):
    sub = uid()
    email = f"ravi.{sub}@example.org"
    fake(monkeypatch, oauth.Identity("google", sub, email, "Ravi", None))
    google = sign_in(api)
    fake(monkeypatch, oauth.Identity("github", sub, email.upper(), "Ravi", f"ravi{sub}"))
    github = sign_in(api, "github")
    assert github["user"]["id"] == google["user"]["id"] and github["new"] is False
    with Session(engine) as s:
        rows = s.exec(select(UserIdentity).where(UserIdentity.user_id == google["user"]["id"])).all()
        assert sorted(r.provider for r in rows) == ["github", "google"]


def test_unverified_email_never_links(api, keys, monkeypatch):
    sub = uid()
    fake(monkeypatch, oauth.Identity("google", sub, f"asha.{sub}@example.org", "Asha", None))
    google = sign_in(api)
    fake(monkeypatch, oauth.Identity("github", sub, None, "Asha", f"asha{sub}"))  # no verified email at GitHub
    github = sign_in(api, "github")
    assert github["user"]["id"] != google["user"]["id"] and github["new"] is True


def test_usernames_never_clash(api, keys, monkeypatch):
    login = f"dev{uid()}"
    fake(monkeypatch, oauth.Identity("github", uid(), None, None, login))
    a = sign_in(api, "github")
    fake(monkeypatch, oauth.Identity("github", uid(), None, None, login))
    b = sign_in(api, "github")
    assert a["user"]["username"] == login and b["user"]["username"] == f"{login}2"


def test_invite_only_site_refuses_new_people_but_not_known_ones(api, keys, monkeypatch):
    sub = uid()
    fake(monkeypatch, oauth.Identity("google", sub, f"known.{sub}@example.org", None, None))
    known = sign_in(api)
    monkeypatch.setenv("ALLOW_SIGNUP", "false")
    get_settings.cache_clear()
    assert sign_in(api)["user"]["id"] == known["user"]["id"]
    fake(monkeypatch, oauth.Identity("google", uid(), None, None, "stranger"))
    assert sign_in(api) == {"error": "closed"}


def test_state_and_code_are_single_use_and_checked(api, keys, monkeypatch):
    fake(monkeypatch, oauth.Identity("google", uid(), None, None, "once"))
    # A callback this browser did not start (no cookie, or a made-up state) is refused.
    bad = api.get("/api/auth/oauth/google/callback", params={"code": "x", "state": "made-up"})
    assert "oauth_error=expired" in bad.headers["location"]
    # The provider said no.
    api.get("/api/auth/oauth/google/start")
    no = api.get("/api/auth/oauth/google/callback", params={"error": "access_denied"})
    assert "oauth_error=cancelled" in no.headers["location"]
    # A state works once; the one-time code works once.
    start = api.get("/api/auth/oauth/google/start")
    state = parse_qs(urlparse(start.headers["location"]).query)["state"][0]
    ok = api.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
    code = parse_qs(urlparse(ok.headers["location"]).query)["oauth"][0]
    api.cookies.set("labbox_oauth", state, path="/api/auth/oauth/google")
    again = api.get("/api/auth/oauth/google/callback", params={"code": "c", "state": state})
    assert "oauth_error=expired" in again.headers["location"]
    assert api.post("/api/auth/oauth/exchange", json={"code": code}).status_code == 200
    assert api.post("/api/auth/oauth/exchange", json={"code": code}).status_code == 401


def test_next_never_leaves_the_site():
    assert oauth.safe_next("//evil.example") == "/labs"
    assert oauth.safe_next("https://evil.example") == "/labs"
    assert oauth.safe_next("/\\evil") == "/labs"
    assert oauth.safe_next("/courses/rag") == "/courses/rag"


def test_password_sign_in_off_unless_switched_on(api, monkeypatch):
    """Google and GitHub only (owner, 27 November): with PASSWORD_LOGIN off, the username form's API refuses."""
    monkeypatch.setenv("PASSWORD_LOGIN", "false")
    get_settings.cache_clear()
    try:
        assert api.get("/api/auth/options").json()["password"] is False
        assert api.post("/api/auth/signup", json={"username": f"nope{uid()}", "password": "secret123"}).status_code == 403
        assert api.post("/api/auth/login", json={"username": "gaurav", "password": "whatever1"}).status_code == 403
    finally:
        monkeypatch.setenv("PASSWORD_LOGIN", "true")
        get_settings.cache_clear()


def test_link_email_and_invite_open_the_right_account(api, keys, monkeypatch):
    """An existing account gets an email (link-email); an invite makes one in advance. Google sign-in with that email
    then opens it, even on an invite-only site."""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("labbox_cli", Path(__file__).resolve().parents[2] / "tools" / "labbox_cli.py")
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    name, email = f"old{uid()}", f"old.{uid()}@example.org"
    old = api.post("/api/auth/signup", json={"username": name, "password": "secret123"}).json()
    assert cli.main(["link-email", name, email.upper()]) == 0
    assert cli.main(["link-email", "no-such-account-x", f"x{uid()}@example.org"]) == 1
    monkeypatch.setenv("ALLOW_SIGNUP", "false")
    get_settings.cache_clear()
    fake(monkeypatch, oauth.Identity("google", uid(), email, None, None))
    assert sign_in(api)["user"]["id"] == old["user"]["id"]
    guest = f"guest.{uid()}@example.org"
    assert cli.main(["invite", guest]) == 0
    assert cli.main(["invite", guest]) == 0  # again: already invited
    fake(monkeypatch, oauth.Identity("github", uid(), guest, "Guest", "guesthub"))
    got = sign_in(api, "github")
    assert got["new"] is False and got["user"]["username"].startswith("guest")
