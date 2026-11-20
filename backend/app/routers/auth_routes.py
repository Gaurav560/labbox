from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import auth, limits, metrics, shared
from ..config import get_settings
from ..db import get_session
from ..models import User

router = APIRouter(prefix="/api", tags=["auth"])


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=72)


class UserOut(BaseModel):
    id: int
    username: str


class TokenOut(BaseModel):
    token: str
    user: UserOut


def _token_out(user: User) -> TokenOut:
    assert user.id is not None
    return TokenOut(token=auth.create_token(user), user=UserOut(id=user.id, username=user.username))


@router.post("/auth/signup", response_model=TokenOut)
def signup(body: Credentials, request: Request, session: Session = Depends(get_session)) -> TokenOut:
    s = get_settings()
    if not s.ALLOW_SIGNUP:
        raise HTTPException(403, "Sign up is disabled")
    key = f"signup:ip:{limits.client_ip(request)}"
    limits.too_many(key, s.SIGNUPS_PER_IP_HOUR, 3600, "Too many new accounts from your network. Try again in an hour.")
    out = _token_out(auth.create_user(session, body.username, body.password))
    shared.hit(key, 3600)  # only accounts that were really made count
    metrics.count("labbox_signups_total")
    return out


@router.post("/auth/login", response_model=TokenOut)
def login(body: Credentials, request: Request, session: Session = Depends(get_session)) -> TokenOut:
    s = get_settings()
    by_ip, by_name = f"loginfail:ip:{limits.client_ip(request)}", f"loginfail:user:{body.username.lower()}"
    wait = "Too many wrong passwords. Wait a minute and try again."
    limits.too_many(by_ip, s.LOGIN_FAILS_PER_IP_MINUTE, 60, wait)
    limits.too_many(by_name, s.LOGIN_FAILS_PER_USER_MINUTE, 60, wait)
    try:
        user = auth.authenticate(session, body.username, body.password)
    except HTTPException:
        shared.hit(by_ip)  # only failed attempts count: a learner logging in often is never slowed down
        shared.hit(by_name)
        metrics.count("labbox_logins_total", result="wrong")
        raise
    metrics.count("labbox_logins_total", result="ok")
    return _token_out(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(auth.get_current_user)) -> UserOut:
    assert user.id is not None
    return UserOut(id=user.id, username=user.username)
