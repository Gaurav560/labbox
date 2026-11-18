from fastapi import APIRouter, Depends, Request, Response, WebSocket
from pydantic import BaseModel

from .. import preview
from ..auth import get_current_user
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
