"""The Library (owner, 24 November): books, research papers and tech blogs worth reading next to the labs.
The list is public (anyone can read it, as with the catalog; the page is used for marketing); only admins can add,
change, reorder or remove items, and every change is logged with the admin's name."""
import base64
import binascii
import hashlib
import io
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session, col, select

from ..config import BACKEND_DIR, get_settings
from ..db import get_session
from ..labs import all_labs
from ..models import LibraryItem, User, utcnow
from .admin_routes import require_admin

log = logging.getLogger("labbox.library")

SEED_IMAGES = BACKEND_DIR.parent / "library" / "images"  # the starting list's pictures, in the repository
IMAGE_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,80}\.webp$")
MAX_UPLOAD = 6 * 1024 * 1024  # bytes, before base64

Kind = Literal["book", "paper", "blog"]
Level = Literal["", "beginner", "intermediate", "advanced"]


class LibraryItemOut(BaseModel):
    id: int
    kind: Kind
    title: str
    authors: str
    year: int | None
    url: str
    note: str
    topic: str
    lab: str
    practice: str
    level: Level
    free: bool
    featured: bool
    image: str
    position: int
    updated_at: datetime


class LibraryItemIn(BaseModel):
    kind: Kind
    title: str = Field(min_length=1, max_length=200)
    authors: str = Field("", max_length=200)
    year: int | None = Field(None, ge=1000, le=2100)
    url: str = Field("", max_length=500)
    note: str = Field("", max_length=1000)
    topic: str = Field("", max_length=40)
    lab: str = Field("", max_length=60)
    practice: str = Field("", max_length=80)
    level: Level = ""
    free: bool = False
    featured: bool = False

    @field_validator("title", "authors", "note", "topic", "practice")
    @classmethod
    def _squeeze(cls, v: str) -> str:
        return " ".join(v.split())

    @field_validator("url")
    @classmethod
    def _http_only(cls, v: str) -> str:
        v = v.strip()
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("The link must start with https:// or http://")
        return v

    @field_validator("lab")
    @classmethod
    def _known_lab(cls, v: str) -> str:
        if v and v not in {lab.id for lab in all_labs()}:
            raise ValueError(f"No lab called {v!r}")
        return v


class ImageIn(BaseModel):
    data: str = Field(min_length=1, max_length=MAX_UPLOAD * 4 // 3 + 8)  # the file, base64 (a data: URL is fine too)


class Move(BaseModel):
    direction: Literal["up", "down"]


def _ordered(session: Session, kind: str | None = None) -> list[LibraryItem]:
    query = select(LibraryItem)
    if kind:
        query = query.where(LibraryItem.kind == kind)
    return list(session.exec(query.order_by(col(LibraryItem.kind), col(LibraryItem.position), col(LibraryItem.id))))


def _only_featured(session: Session, item: LibraryItem) -> None:
    """One "Start here" pick per section: featuring an item unfeatures the others of its kind."""
    if item.featured:
        for other in _ordered(session, item.kind):
            if other.id != item.id and other.featured:
                other.featured = False
                session.add(other)


def _get(session: Session, item_id: int) -> LibraryItem:
    item = session.get(LibraryItem, item_id)
    if item is None:
        raise HTTPException(404, "No such library item")
    return item


router = APIRouter(prefix="/api/library", tags=["library"])


def _image_path(name: str) -> Path | None:
    if not IMAGE_NAME.match(name):
        return None
    for folder in (get_settings().LIBRARY_UPLOADS_DIR, SEED_IMAGES):
        path = folder / name
        if path.is_file():
            return path
    return None


@router.get("/images/{name}", include_in_schema=False)
def image(name: str) -> FileResponse:
    """A Library picture, stored with LabBox (nothing is fetched from other sites when a page opens)."""
    path = _image_path(name)
    if path is None:
        raise HTTPException(404, "No such picture")
    return FileResponse(path, media_type="image/webp", headers={"Cache-Control": "public, max-age=604800"})


@router.get("", response_model=list[LibraryItemOut])
def library(session: Session = Depends(get_session)) -> list[LibraryItem]:
    """Every item, grouped by kind (book, paper, blog) and in the admins' order. Public: no login needed."""
    return _ordered(session)


admin_router = APIRouter(prefix="/api/admin/library", tags=["admin"], dependencies=[Depends(require_admin)])


@admin_router.post("", response_model=LibraryItemOut, status_code=201)
def add(body: LibraryItemIn, admin: User = Depends(require_admin), session: Session = Depends(get_session)) -> LibraryItem:
    last = _ordered(session, body.kind)
    item = LibraryItem(**body.model_dump(), position=(last[-1].position + 1) if last else 0)
    session.add(item)
    session.flush()
    _only_featured(session, item)
    session.commit()
    session.refresh(item)
    log.warning("Admin %s added library %s %d: %s", admin.username, item.kind, item.id, item.title)
    return item


@admin_router.put("/{item_id}", response_model=LibraryItemOut)
def change(item_id: int, body: LibraryItemIn, admin: User = Depends(require_admin),
           session: Session = Depends(get_session)) -> LibraryItem:
    item = _get(session, item_id)
    if body.kind != item.kind:  # moving to another list: go to its end
        last = _ordered(session, body.kind)
        item.position = (last[-1].position + 1) if last else 0
    for key, value in body.model_dump().items():
        setattr(item, key, value)
    item.updated_at = utcnow()
    session.add(item)
    _only_featured(session, item)
    session.commit()
    session.refresh(item)
    log.warning("Admin %s changed library item %d: %s", admin.username, item.id, item.title)
    return item


@admin_router.post("/{item_id}/move", response_model=list[LibraryItemOut])
def move(item_id: int, body: Move, admin: User = Depends(require_admin),
         session: Session = Depends(get_session)) -> list[LibraryItem]:
    """Swaps an item with its neighbour in the same list; returns that list in its new order."""
    item = _get(session, item_id)
    items = _ordered(session, item.kind)
    for position, entry in enumerate(items):  # make positions 0, 1, 2, ... first, so a swap always works
        entry.position = position
    i = next(n for n, entry in enumerate(items) if entry.id == item.id)
    j = i - 1 if body.direction == "up" else i + 1
    if 0 <= j < len(items):
        items[i].position, items[j].position = items[j].position, items[i].position
    for entry in items:
        session.add(entry)
    session.commit()
    log.warning("Admin %s moved library item %d %s", admin.username, item.id, body.direction)
    return _ordered(session, item.kind)


@admin_router.delete("/{item_id}")
def remove(item_id: int, admin: User = Depends(require_admin), session: Session = Depends(get_session)) -> dict:
    item = _get(session, item_id)
    session.delete(item)
    session.commit()
    log.warning("Admin %s removed library item %d: %s", admin.username, item_id, item.title)
    return {"ok": True}


@admin_router.put("/{item_id}/image", response_model=LibraryItemOut)
def upload_image(item_id: int, body: ImageIn, admin: User = Depends(require_admin),
                 session: Session = Depends(get_session)) -> LibraryItem:
    """A picture for an item: any common image format, checked, resized and stored as WebP with LabBox."""
    item = _get(session, item_id)
    raw = body.data.split(",", 1)[1] if body.data.startswith("data:") else body.data
    try:
        data = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(422, "The picture could not be read (send the file as base64)") from None
    if len(data) > MAX_UPLOAD:
        raise HTTPException(413, "The picture is larger than 6 MB")
    try:
        with Image.open(io.BytesIO(data)) as picture:
            picture.load()
            picture = picture.convert("RGB")
            picture.thumbnail((800, 800))
            out = io.BytesIO()
            picture.save(out, "WEBP", quality=84)
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise HTTPException(422, "That file is not a picture LabBox can read (use JPEG, PNG or WebP)") from None
    folder = get_settings().LIBRARY_UPLOADS_DIR
    folder.mkdir(parents=True, exist_ok=True)
    name = f"upload-{item.id}-{hashlib.sha256(out.getvalue()).hexdigest()[:12]}.webp"
    (folder / name).write_bytes(out.getvalue())
    item.image = name
    item.updated_at = utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    log.warning("Admin %s set the picture of library item %d", admin.username, item.id)
    return item


@admin_router.delete("/{item_id}/image", response_model=LibraryItemOut)
def remove_image(item_id: int, admin: User = Depends(require_admin), session: Session = Depends(get_session)) -> LibraryItem:
    item = _get(session, item_id)
    item.image = ""
    item.updated_at = utcnow()
    session.add(item)
    session.commit()
    session.refresh(item)
    log.warning("Admin %s removed the picture of library item %d", admin.username, item.id)
    return item
