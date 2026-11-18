from fastapi import APIRouter, Query, WebSocket

from ..terminal import run_terminal

router = APIRouter(tags=["terminal"])


@router.websocket("/ws/terminal/{lab_id}")
async def terminal(ws: WebSocket, lab_id: str, token: str | None = Query(None)) -> None:
    await run_terminal(ws, lab_id, token)
