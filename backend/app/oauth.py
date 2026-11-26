"""Sign in with Google and GitHub (owner, 27 November; Phase H4's social login).

The flow, for each provider:
1. /api/auth/oauth/<provider>/start: a random `state`, kept on the server for 10 minutes and in a short cookie (so the
   sign-in that comes back is the one this browser started), and for Google a PKCE verifier; then off to the provider.
2. The provider sends the learner back to /api/auth/oauth/<provider>/callback with a code. The server checks the state
   against its record and the cookie, swaps the code for the person's identity (`fetch_identity`, the only network
   part), and finds or makes the LabBox account:
   - the same provider account always signs into the same LabBox account (user_identity);
   - otherwise a LabBox account with the same verified email gets this provider account linked to it;
   - otherwise, when sign-up is open, a new account (a username from the provider, no password; onboarding follows).
3. The callback sends the browser to /login?oauth=<one-time code>, never with the login token in the address. The page
   swaps the code (good once, for 60 seconds) for the same login token a password login gives.
"""
import base64
import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException
from sqlmodel import Session, func, select

from . import auth, shared
from .config import get_settings
from .models import User, UserIdentity, UserProfile, utcnow

Provider = Literal["google", "github"]
PROVIDERS: tuple[Provider, ...] = ("google", "github")
STATE_SECONDS = 600
CODE_SECONDS = 60
COOKIE = "labbox_oauth"
TIMEOUT = 15


@dataclass
class Identity:
    provider: Provider
    subject: str
    email: str | None  # only a verified address
    name: str | None
    login: str | None  # a username hint (GitHub login, or the email's first part)


class OAuthError(Exception):
    """A sign-in that cannot finish; `reason` becomes ?oauth_error=<reason> on the login page."""

    def __init__(self, reason: Literal["cancelled", "failed", "expired", "closed"]):
        super().__init__(reason)
        self.reason = reason


def configured() -> list[Provider]:
    s = get_settings()
    out: list[Provider] = []
    if s.GOOGLE_CLIENT_ID and s.GOOGLE_CLIENT_SECRET:
        out.append("google")
    if s.GITHUB_CLIENT_ID and s.GITHUB_CLIENT_SECRET:
        out.append("github")
    return out


def require(provider: str) -> Provider:
    if provider not in configured():
        raise HTTPException(404, "This sign-in is not set up")
    return provider  # type: ignore[return-value]


def redirect_uri(base: str, provider: Provider) -> str:
    return f"{(get_settings().PUBLIC_URL or base).rstrip('/')}/api/auth/oauth/{provider}/callback"


def safe_next(raw: str | None) -> str:
    """Where to land after signing in: a path on this site, never another site."""
    return raw if raw and raw.startswith("/") and not raw.startswith("//") and not raw.startswith("/\\") else "/labs"


# ---------- 1. start ----------

def start(provider: Provider, base: str, next_path: str | None) -> tuple[str, str]:
    """The provider's sign-in address and the state (also set as a cookie by the route)."""
    s = get_settings()
    state = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(48)
    shared.put(f"oauth:state:{state}", json.dumps({"provider": provider, "verifier": verifier, "next": safe_next(next_path)}),
               STATE_SECONDS)
    if provider == "google":
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        q = {"client_id": s.GOOGLE_CLIENT_ID, "redirect_uri": redirect_uri(base, provider), "response_type": "code",
             "scope": "openid email profile", "state": state, "code_challenge": challenge,
             "code_challenge_method": "S256", "prompt": "select_account"}
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(q)}", state
    q = {"client_id": s.GITHUB_CLIENT_ID, "redirect_uri": redirect_uri(base, provider), "scope": "read:user user:email",
         "state": state, "allow_signup": "true"}
    return f"https://github.com/login/oauth/authorize?{urlencode(q)}", state


# ---------- 2. callback ----------

def take_state(provider: Provider, state: str | None, cookie: str | None) -> dict:
    if not state or not cookie or not secrets.compare_digest(state, cookie):
        raise OAuthError("expired")
    raw = shared.get(f"oauth:state:{state}")
    shared.delete(f"oauth:state:{state}")
    if raw is None:
        raise OAuthError("expired")
    saved = json.loads(raw)
    if saved.get("provider") != provider:
        raise OAuthError("expired")
    return saved


def fetch_identity(provider: Provider, code: str, verifier: str, uri: str) -> Identity:
    """Swap the code for the person's identity at the provider (the network part; tests replace it)."""
    s = get_settings()
    try:
        with httpx.Client(timeout=TIMEOUT, headers={"Accept": "application/json", "User-Agent": "LabBox"}) as c:
            if provider == "google":
                tok = c.post("https://oauth2.googleapis.com/token", data={
                    "code": code, "client_id": s.GOOGLE_CLIENT_ID, "client_secret": s.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": uri, "grant_type": "authorization_code", "code_verifier": verifier}).json()
                access = tok.get("access_token")
                if not access:
                    raise OAuthError("failed")
                me = c.get("https://openidconnect.googleapis.com/v1/userinfo",
                           headers={"Authorization": f"Bearer {access}"}).json()
                if not me.get("sub"):
                    raise OAuthError("failed")
                email = me.get("email") if me.get("email_verified") else None
                return Identity("google", str(me["sub"]), email, me.get("name"), (email or "").split("@")[0] or None)
            tok = c.post("https://github.com/login/oauth/access_token", data={
                "code": code, "client_id": s.GITHUB_CLIENT_ID, "client_secret": s.GITHUB_CLIENT_SECRET,
                "redirect_uri": uri}).json()
            access = tok.get("access_token")
            if not access:
                raise OAuthError("failed")
            h = {"Authorization": f"Bearer {access}", "Accept": "application/vnd.github+json"}
            me = c.get("https://api.github.com/user", headers=h).json()
            if not me.get("id"):
                raise OAuthError("failed")
            emails = c.get("https://api.github.com/user/emails", headers=h).json()
            primary = next((e["email"] for e in emails if isinstance(e, dict) and e.get("primary") and e.get("verified")), None) \
                if isinstance(emails, list) else None
            return Identity("github", str(me["id"]), primary, me.get("name"), me.get("login"))
    except httpx.HTTPError:
        raise OAuthError("failed")


def _free_username(session: Session, hint: str | None) -> str:
    base = re.sub(r"[^A-Za-z0-9_.-]", "", (hint or "").strip())[:24].strip(".-_") or "learner"
    if len(base) < 3:
        base = f"{base}learner"
    name, n = base, 1
    while session.exec(select(User).where(func.lower(User.username) == name.lower())).first() is not None:
        n += 1
        name = f"{base}{n}"
    return name


def account_for(session: Session, ident: Identity, ip_key: str) -> tuple[User, bool]:
    """The LabBox account this identity signs into, and whether it was just made."""
    now = utcnow()
    link = session.exec(select(UserIdentity).where(UserIdentity.provider == ident.provider,
                                                   UserIdentity.subject == ident.subject)).first()
    user = session.get(User, link.user_id) if link else None
    email = ident.email.strip().lower() if ident.email else None
    if user is None and email:
        user = session.exec(select(User).where(func.lower(User.email) == email)).first()
    made = False
    if user is None:
        s = get_settings()
        if not s.ALLOW_SIGNUP:
            raise OAuthError("closed")
        from . import limits

        limits.too_many(ip_key, s.SIGNUPS_PER_IP_HOUR, 3600, "Too many new accounts from your network. Try again in an hour.")
        user = User(username=_free_username(session, ident.login), password_hash=auth.hash_password(secrets.token_urlsafe(32)))
        made = True
    if email and not user.email and session.exec(select(User).where(func.lower(User.email) == email)).first() is None:
        user.email, user.email_verified_at = email, now
    session.add(user)
    session.commit()
    session.refresh(user)
    assert user.id is not None
    if made:
        shared.hit(ip_key, 3600)
        if ident.name:
            session.add(UserProfile(user_id=user.id, display_name=ident.name.strip()[:60]))
    if link is None:
        link = UserIdentity(user_id=user.id, provider=ident.provider, subject=ident.subject, email=email)
    link.last_login_at = now
    link.email = email or link.email
    session.add(link)
    session.commit()
    return user, made


def one_time_code(user_id: int, made: bool) -> str:
    code = secrets.token_urlsafe(24)
    shared.put(f"oauth:code:{code}", json.dumps({"user": user_id, "new": made}), CODE_SECONDS)
    return code


# ---------- 3. the page swaps the code for a login ----------

def redeem(session: Session, code: str) -> tuple[User, bool]:
    raw = shared.get(f"oauth:code:{code}")
    shared.delete(f"oauth:code:{code}")
    user = session.get(User, json.loads(raw)["user"]) if raw else None
    if user is None:
        raise HTTPException(401, "This sign-in link has expired. Try again.")
    return user, bool(json.loads(raw or "{}").get("new"))
