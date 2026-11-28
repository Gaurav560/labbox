"""Lostdesk, chapter 16: passwords and tokens. Staff sign in with a password and get a token."""
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from pydantic import BaseModel

# A real service reads the secret from the environment (chapter 19). Never put a real secret in code.
SECRET_KEY = "lostdesk-course-secret-not-for-production-7d1f0c2a9b"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


DUMMY_HASH = hash_password("not-a-real-password")

STAFF = {
    "meera": {"username": "meera", "full_name": "Meera Joshi", "desk": "Riverside", "role": "clerk",
              "hashed_password": hash_password("riverside-umbrella-42")},
    "arjun": {"username": "arjun", "full_name": "Arjun Rao", "desk": "Airport", "role": "supervisor",
              "hashed_password": hash_password("airport-keys-77")},
}


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate(username: str, password: str) -> dict | None:
    """The staff member, when the password is right; None otherwise."""
    user = STAFF.get(username)
    if user is None:
        verify_password(password, DUMMY_HASH)  # take as long as a real check, so timing gives nothing away
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(username: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


app = FastAPI()


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(user["username"]), token_type="bearer")
