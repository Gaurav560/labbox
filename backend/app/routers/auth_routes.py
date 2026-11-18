from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import auth
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
def signup(body: Credentials, session: Session = Depends(get_session)) -> TokenOut:
    if not get_settings().ALLOW_SIGNUP:
        raise HTTPException(403, "Sign up is disabled")
    return _token_out(auth.create_user(session, body.username, body.password))


@router.post("/auth/login", response_model=TokenOut)
def login(body: Credentials, session: Session = Depends(get_session)) -> TokenOut:
    return _token_out(auth.authenticate(session, body.username, body.password))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(auth.get_current_user)) -> UserOut:
    assert user.id is not None
    return UserOut(id=user.id, username=user.username)
