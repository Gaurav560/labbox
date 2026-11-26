"""WebSocket <-> docker exec bridge for the in-browser terminal."""
import asyncio
import json
import logging
import time

from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from sqlmodel import Session
from starlette.websockets import WebSocketState

from . import containers, slots
from .auth import user_from_token
from .db import engine
from .labs import get_lab

log = logging.getLogger(__name__)

RECV_BYTES = 4096
MAX_INPUT_CHARS = 64 * 1024
CLOSE_UNAUTHORIZED = 4401
CLOSE_NOT_FOUND = 4404
CLOSE_ERROR = 1011


async def _fail(ws: WebSocket, code: int, message: str) -> None:
    await ws.send_json({"type": "error", "message": message})
    await ws.close(code=code)


async def run_terminal(ws: WebSocket, lab_id: str, token: str | None) -> None:
    # Accept first: closing before accept would send a plain HTTP 403 and lose our close code.
    await ws.accept()
    with Session(engine) as session:
        user = user_from_token(token, session) if token else None
        if user is None:
            await _fail(ws, CLOSE_UNAUTHORIZED, "Not authenticated")
            return
        try:
            lab = get_lab(lab_id)
            slots.require_open(session, user, lab)
            workspace = await asyncio.to_thread(containers.ensure_workspace, session, user, lab)
            exec_id, raw, session_file = await asyncio.to_thread(containers.open_shell, lab, workspace)
        except HTTPException as e:
            await _fail(ws, CLOSE_NOT_FOUND if e.status_code == 404 else CLOSE_ERROR, str(e.detail))
            return

        log.info("Terminal opened user=%s lab=%s exec=%s", user.id, lab.id, exec_id[:12])
        await ws.send_json({"type": "status", "message": "connected"})
        last_touch = time.monotonic()

        async def container_to_browser() -> None:
            while True:
                try:
                    data = await asyncio.to_thread(raw.recv, RECV_BYTES)
                except OSError:
                    data = b""
                if not data:
                    await ws.send_json({"type": "exit"})
                    return
                await ws.send_bytes(data)

        async def browser_to_container() -> None:
            nonlocal last_touch
            while True:
                text = await ws.receive_text()
                try:
                    msg = json.loads(text)
                except ValueError:
                    continue
                if not isinstance(msg, dict):
                    continue
                kind = msg.get("type")
                if kind == "input" and isinstance(msg.get("data"), str):
                    await asyncio.to_thread(raw.sendall, msg["data"][:MAX_INPUT_CHARS].encode())
                elif kind == "resize":
                    try:
                        cols = max(1, min(500, int(msg["cols"])))
                        rows = max(1, min(200, int(msg["rows"])))
                    except (KeyError, TypeError, ValueError):
                        continue
                    await asyncio.to_thread(containers.resize_shell, exec_id, cols, rows)
                elif kind == "ping":
                    await ws.send_json({"type": "pong"})
                if time.monotonic() - last_touch >= containers.TOUCH_MIN_SECONDS:
                    last_touch = time.monotonic()
                    await asyncio.to_thread(containers.touch, session, workspace)

        tasks = [asyncio.create_task(container_to_browser()), asyncio.create_task(browser_to_container())]
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                exc = t.exception()
                if exc and not isinstance(exc, (WebSocketDisconnect, RuntimeError)):
                    log.warning("Terminal task ended with %r", exc)
        finally:
            for t in tasks:
                t.cancel()
            await asyncio.to_thread(containers.close_shell, workspace.container_name, raw, session_file)
            await asyncio.gather(*tasks, return_exceptions=True)
            if ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.close()
                except RuntimeError:
                    pass
            log.info("Terminal closed user=%s lab=%s", user.id, lab.id)
