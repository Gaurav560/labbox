from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlmodel import Session

from .. import containers
from .. import workspace_files as wf
from ..auth import get_current_user
from ..config import get_settings
from ..db import get_session
from ..labs import get_lab
from ..models import User, Workspace

router = APIRouter(prefix="/api/labs/{lab_id}/files", tags=["files"])


class FileContent(BaseModel):
    path: str
    content: str


class Saved(BaseModel):
    saved: bool
    bytes: int


class NewEntry(BaseModel):
    path: str = Field(min_length=1)
    type: Literal["file", "dir"]


class RenameBody(BaseModel):
    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)


class Flag(BaseModel):
    created: bool | None = None
    renamed: bool | None = None
    deleted: bool | None = None


def workspace(lab_id: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> Workspace:
    """The current user's workspace for this lab. user_id always comes from the JWT."""
    return containers.get_workspace(session, user, get_lab(lab_id))


def active_workspace(ws: Workspace = Depends(workspace), session: Session = Depends(get_session)) -> Workspace:
    containers.touch(session, ws, force=False)
    return ws


def root(ws: Workspace) -> Path:
    return Path(ws.volume_path)


# The tree is polled by the UI, so listing it does not count as activity for the idle reaper.
@router.get("", response_model=list[wf.FileNode], response_model_exclude_none=True)
def tree(ws: Workspace = Depends(workspace)) -> list[wf.FileNode]:
    return wf.list_tree(root(ws))


@router.get("/content", response_model=FileContent)
def read(path: str = Query(...), ws: Workspace = Depends(active_workspace)) -> FileContent:
    return FileContent(path=path, content=wf.read_file(root(ws), path, get_settings().MAX_FILE_BYTES))


@router.put("/content", response_model=Saved)
def write(body: FileContent, ws: Workspace = Depends(active_workspace)) -> Saved:
    n = wf.write_file(root(ws), body.path, body.content, get_settings().MAX_FILE_BYTES)
    return Saved(saved=True, bytes=n)


@router.post("/new", response_model=Flag, response_model_exclude_none=True)
def new(body: NewEntry, ws: Workspace = Depends(active_workspace)) -> Flag:
    wf.create(root(ws), body.path, body.type)
    return Flag(created=True)


@router.post("/rename", response_model=Flag, response_model_exclude_none=True)
def rename(body: RenameBody, ws: Workspace = Depends(active_workspace)) -> Flag:
    wf.rename(root(ws), body.from_, body.to)
    return Flag(renamed=True)


@router.delete("", response_model=Flag, response_model_exclude_none=True)
def delete(path: str = Query(...), ws: Workspace = Depends(active_workspace)) -> Flag:
    wf.delete(root(ws), path)
    return Flag(deleted=True)
