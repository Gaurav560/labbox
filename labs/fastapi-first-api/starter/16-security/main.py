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


# TODO (task hash_passwords): hash_password gives back password_hash's hash of the password; verify_password says
# whether a password matches a hash. Never store or compare the password itself.
def hash_password(password: str) -> str:
    return password


def verify_password(password: str, hashed: str) -> bool:
    return password == hashed


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
    # TODO (task hash_passwords): give back the staff member when the password matches their hashed_password, else None.
    # For an unknown username, still check the password against DUMMY_HASH, so both cases take as long.
    return None


def create_access_token(username: str) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


app = FastAPI()


# TODO (task login_token): POST /token reads the login form (OAuth2PasswordRequestForm), authenticates the user, and
# gives back a Token: an access token made by create_access_token and the type "bearer". A wrong username or
# password gives 401 with the header WWW-Authenticate: Bearer.
