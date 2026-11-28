"""Lostdesk, chapter 17: protecting routes. The token says who you are; your role says what you may do."""
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

SECRET_KEY = "lostdesk-course-secret-not-for-production-7d1f0c2a9b"
ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 30

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("not-a-real-password")

STAFF = {
    "meera": {"username": "meera", "full_name": "Meera Joshi", "desk": "Riverside", "role": "clerk",
              "hashed_password": password_hash.hash("riverside-umbrella-42")},
    "arjun": {"username": "arjun", "full_name": "Arjun Rao", "desk": "Airport", "role": "supervisor",
              "hashed_password": password_hash.hash("airport-keys-77")},
}

FOUND = {1: {"id": 1, "title": "black umbrella"}, 2: {"id": 2, "title": "blue school bag"}}


class Token(BaseModel):
    access_token: str
    token_type: str


class StaffPublic(BaseModel):
    username: str
    full_name: str
    desk: str
    role: str


def authenticate(username: str, password: str) -> dict | None:
    user = STAFF.get(username)
    if user is None:
        password_hash.verify(password, DUMMY_HASH)
        return None
    if not password_hash.verify(password, user["hashed_password"]):
        return None
    return user


def create_access_token(username: str, minutes: int = ACCESS_TOKEN_MINUTES) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=minutes)
    return jwt.encode({"sub": username, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# TODO (task current_user): get_current_user takes the token (Depends(oauth2_scheme)), decodes it with SECRET_KEY and
# ALGORITHM, and gives back the staff member named in "sub". A token that cannot be decoded (wrong, changed or expired),
# or names nobody, gives 401 with the header WWW-Authenticate: Bearer.
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    return STAFF["meera"]


CurrentUser = Annotated[dict, Depends(get_current_user)]


# TODO (task supervisor_only): require_supervisor gives back the current user when their role is supervisor, and
# answers 403 otherwise. Then guard DELETE /items/{item_id} with it.
def require_supervisor(user: CurrentUser) -> dict:
    return user


app = FastAPI()


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(status_code=401, detail="Wrong username or password", headers={"WWW-Authenticate": "Bearer"})
    return Token(access_token=create_access_token(user["username"]), token_type="bearer")


@app.get("/me")
def read_me(user: CurrentUser) -> StaffPublic:
    return user


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int):
    if item_id not in FOUND:
        raise HTTPException(status_code=404, detail="No item with that id")
    del FOUND[item_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
