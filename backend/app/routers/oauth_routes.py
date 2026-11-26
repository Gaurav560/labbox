"""Sign in with Google and GitHub (owner, 27 November; the flow is in app/oauth.py)."""
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session

from .. import limits, metrics, oauth
from ..db import get_session
from .auth_routes import TokenOut, _token_out

router = APIRouter(prefix="/api/auth/oauth", tags=["auth"])


def _base(request: Request) -> str:
    """The address the visitor used (Caddy and Vite's proxy say it in X-Forwarded-Host)."""
    host = request.headers.get("x-forwarded-host") or request.headers.get("host") or request.url.netloc
    proto = request.headers.get("x-forwarded-proto") or request.url.scheme
    return f"{proto.split(',')[0].strip()}://{host.split(',')[0].strip()}"


def _cookie_path(provider: str) -> str:
    return f"/api/auth/oauth/{provider}"


@router.get("/{provider}/start", include_in_schema=False)
def start(provider: str, request: Request, next: str | None = None) -> RedirectResponse:
    p = oauth.require(provider)
    url, state = oauth.start(p, _base(request), next)
    r = RedirectResponse(url, status_code=302)
    r.set_cookie(oauth.COOKIE, state, max_age=oauth.STATE_SECONDS, httponly=True, samesite="lax",
                 secure=_base(request).startswith("https://"), path=_cookie_path(p))
    return r


@router.get("/{provider}/callback", include_in_schema=False)
def callback(provider: str, request: Request, code: str | None = None, state: str | None = None,
             error: str | None = None, session: Session = Depends(get_session)) -> RedirectResponse:
    p = oauth.require(provider)
    try:
        if error:
            raise oauth.OAuthError("cancelled")
        saved = oauth.take_state(p, state, request.cookies.get(oauth.COOKIE))
        if not code:
            raise oauth.OAuthError("failed")
        ident = oauth.fetch_identity(p, code, saved["verifier"], oauth.redirect_uri(_base(request), p))
        user, made = oauth.account_for(session, ident, f"signup:ip:{limits.client_ip(request)}")
        assert user.id is not None
        target = "/login?" + urlencode({"oauth": oauth.one_time_code(user.id, made), "next": saved["next"]})
        metrics.count("labbox_oauth_logins_total", provider=p, result="new" if made else "ok")
    except oauth.OAuthError as e:
        metrics.count("labbox_oauth_logins_total", provider=p, result=e.reason)
        target = "/login?" + urlencode({"oauth_error": e.reason, "provider": p})
    r = RedirectResponse(target, status_code=302)
    r.delete_cookie(oauth.COOKIE, path=_cookie_path(p))
    return r


class ExchangeBody(BaseModel):
    code: str


class ExchangeOut(TokenOut):
    new: bool = False  # the account was just made (the page goes on to onboarding)


@router.post("/exchange", response_model=ExchangeOut)
def exchange(body: ExchangeBody, session: Session = Depends(get_session)) -> ExchangeOut:
    """The one-time code from the callback, swapped (once) for the same login a password gives."""
    user, made = oauth.redeem(session, body.code)
    return ExchangeOut(**_token_out(user).model_dump(), new=made)
