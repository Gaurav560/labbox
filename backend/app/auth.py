from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

from .config import get_settings
from .db import get_session
from .models import User

ALGORITHM = "HS256"
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _pwd.verify(password, password_hash)


def create_token(user: User) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user.id), "exp": expire}, settings.JWT_SECRET, algorithm=ALGORITHM)


def create_scoped_token(user: User, scope: str, minutes: int) -> str:
    """A short-lived token for one purpose only (e.g. the preview cookie). Never valid as a login."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user.id), "scope": scope, "exp": expire}, get_settings().JWT_SECRET, algorithm=ALGORITHM)


def user_from_token(token: str, session: Session, scope: str | None = None) -> User | None:
    """Return the user for a valid token, else None. Used by HTTP and WebSocket auth.

    A login token has no scope; a scoped token is only accepted where that exact scope is asked for.
    """
    try:
        payload = jwt.decode(token, get_settings().JWT_SECRET, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError, TypeError):
        return None
    if payload.get("scope") != scope:
        return None
    return session.get(User, user_id)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: Session = Depends(get_session),
) -> User:
    user = user_from_token(creds.credentials, session) if creds else None
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Not authenticated", headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def create_user(session: Session, username: str, password: str) -> User:
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = User(username=username, password_hash=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate(session: Session, username: str, password: str) -> User:
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong username or password")
    return user
