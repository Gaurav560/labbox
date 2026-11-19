import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request, Response, WebSocket
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlmodel import Session

from .. import containers, ide, preview
from ..auth import get_current_user
from ..config import get_settings
from ..db import get_session
from ..labs import PreviewPort, get_lab
from ..models import User

router = APIRouter(tags=["preview"])


class PreviewInfo(BaseModel):
    ports: list[PreviewPort]


@router.post("/api/labs/{lab_id}/preview/ticket", response_model=PreviewInfo)
def preview_ticket(lab_id: str, response: Response, user: User = Depends(get_current_user)) -> PreviewInfo:
    """Sets the HttpOnly preview cookie for this browser. The lab page calls it when it opens."""
    lab = get_lab(lab_id)
    response.set_cookie(
        preview.COOKIE,
        preview.ticket(user),
        max_age=preview.TICKET_MINUTES * 60,
        httponly=True,
        samesite="strict",
        path="/preview",
    )
    return PreviewInfo(ports=lab.preview)


_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


@router.api_route("/preview/{lab_id}/{port}", methods=_METHODS, include_in_schema=False)
@router.api_route("/preview/{lab_id}/{port}/{path:path}", methods=_METHODS, include_in_schema=False)
async def preview_http(request: Request, lab_id: str, port: int, path: str = ""):
    return await preview.proxy_http(request, lab_id, port, path)


@router.websocket("/preview/{lab_id}/{port}/{path:path}")
async def preview_ws(ws: WebSocket, lab_id: str, port: int, path: str = ""):
    await preview.proxy_ws(ws, lab_id, port, path)


class IdeInfo(BaseModel):
    available: bool  # false: VS Code is not installed or switched off, use the classic editor
    ready: bool = False
    url: str = ""


@router.post("/api/labs/{lab_id}/ide", response_model=IdeInfo)
async def open_ide(lab_id: str, response: Response, user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> IdeInfo:
    """Make sure the machine and its VS Code are running, set the proxy cookie for /ide, return the URL."""
    lab = get_lab(lab_id)
    if not ide.available():
        return IdeInfo(available=False)
    assert user.id is not None
    await asyncio.to_thread(containers.upgrade_for_ide, session, user, lab)
    ws = await asyncio.to_thread(containers.ensure_workspace, session, user, lab)
    await asyncio.to_thread(ide.start, lab, ws)
    ready = await asyncio.to_thread(ide.wait_ready, lab, ws)
    response.set_cookie(preview.COOKIE, preview.ticket(user), max_age=preview.TICKET_MINUTES * 60, httponly=True, samesite="strict", path="/ide")
    return IdeInfo(available=True, ready=ready, url=f"{ide.base_path(lab.id)}/?tkn={ide.token(user.id, lab.id)}&folder=/workspace")


@router.get("/ide-fonts/{name}", include_in_schema=False)
def ide_font(name: str):
    """JetBrains Mono for VS Code's editor and terminal. A fixed list of files, nothing else."""
    path = get_settings().IDE_DIR / "fonts" / name
    if name not in ide.FONT_FILES or not path.is_file():
        raise HTTPException(404, "No such font")
    return FileResponse(path, media_type="font/woff2", headers={"Cache-Control": "public, max-age=604800"})


@router.api_route("/ide/{lab_id}", methods=_METHODS, include_in_schema=False)
@router.api_route("/ide/{lab_id}/{path:path}", methods=_METHODS, include_in_schema=False)
async def ide_http(request: Request, lab_id: str, path: str = ""):
    if not ide.available():
        raise HTTPException(404, "VS Code is not set up on this server")
    return await preview.proxy_http(request, lab_id, ide.PORT, path, full_path=True)


@router.websocket("/ide/{lab_id}/{path:path}")
async def ide_ws(ws: WebSocket, lab_id: str, path: str = ""):
    await preview.proxy_ws(ws, lab_id, ide.PORT, path, full_path=True)
