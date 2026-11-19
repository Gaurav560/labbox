"""Web preview (v2 spec 4.2): /preview/{lab}/{port}/{path} proxies to the learner's own container.

Auth is a short-lived HttpOnly cookie set by the lab page, scoped to "preview" so it is never a
login. The URL has no user id in it: it always resolves to the cookie owner's container, so one
learner cannot reach another learner's app. Only ports listed in the lab's `preview` are allowed.

Production should serve /preview from its own origin (preview.<domain>) so learner JavaScript
cannot touch the main app's storage; in development the same origin is fine (see README).
"""
import asyncio
import logging
from urllib.parse import quote

import httpx
import websockets
from fastapi import HTTPException, Request, WebSocket
from fastapi.responses import Response, StreamingResponse
from sqlmodel import Session
from starlette.background import BackgroundTask

from . import containers, ide, services
from .auth import create_scoped_token, user_from_token
from .db import engine
from .labs import LabConfig, get_lab
from .models import User

log = logging.getLogger(__name__)

COOKIE = "labbox_preview"
SCOPE = "preview"
TICKET_MINUTES = 120
# Hop-by-hop headers (RFC 9110) plus ones we set ourselves.
_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailer",
        "transfer-encoding", "upgrade", "host", "content-length"}

ACTIVITY_MIN_BYTES = 64  # websocket messages smaller than this are keep-alives, not learner activity
ACTIVITY_EVERY_SECONDS = 60

_client: httpx.AsyncClient | None = None


def http_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=3.0), follow_redirects=False)
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def ticket(user: User) -> str:
    return create_scoped_token(user, SCOPE, TICKET_MINUTES)


def _user(cookie: str | None) -> User | None:
    if not cookie:
        return None
    with Session(engine) as session:
        return user_from_token(cookie, session, scope=SCOPE)


def _target(user: User, lab: LabConfig, port: int, any_port: bool = False) -> str:
    """host:port of the learner's workspace, or an HTTP error the browser can show."""
    if not any_port and port not in {p.port for p in lab.preview}:
        raise HTTPException(403, f"Port {port} is not open for preview in this lab")
    assert user.id is not None
    name = containers.container_name(user.id, lab.id)
    net = f"labnet-u{user.id}-{lab.id}" if lab.uses_lab_network else None
    ip = services.container_ip(name, prefer_network=net)
    if ip is None:
        raise HTTPException(503, "Your machine is not running. Start it from the lab page.")
    return f"{ip}:{port}"


def _authorize(request_cookie: str | None, lab_id: str, port: int, any_port: bool = False) -> tuple[User, LabConfig, str]:
    user = _user(request_cookie)
    if user is None:
        raise HTTPException(403, "Open the preview from the lab page (your preview session is missing or expired)")
    lab = get_lab(lab_id)
    return user, lab, _target(user, lab, port, any_port)


def _forward_headers(headers, prefix: str) -> dict[str, str]:
    out = {k: v for k, v in headers.items() if k.lower() not in _HOP and k.lower() != "cookie"}
    # Keep the learner app's own cookies, never ours.
    cookies = [c for c in headers.get("cookie", "").split(";") if c.strip() and not c.strip().startswith(COOKIE + "=")]
    if cookies:
        out["cookie"] = ";".join(cookies)
    out["x-forwarded-prefix"] = prefix
    return out


async def proxy_http(request: Request, lab_id: str, port: int, path: str, full_path: bool = False) -> Response:
    """full_path: forward the whole request path (VS Code knows its base path), not just the tail."""
    user, lab, target = await asyncio.to_thread(_authorize, request.cookies.get(COOKIE), lab_id, port, full_path)
    prefix = f"/ide/{lab_id}" if full_path else f"/preview/{lab_id}/{port}"
    url = f"http://{target}{quote(request.url.path)}" if full_path else f"http://{target}/{quote(path)}"
    if request.url.query:
        url += "?" + request.url.query
    client = http_client()
    headers_out = _forward_headers(request.headers, prefix)
    start_page = full_path and request.method == "GET" and ide.is_start_page(lab_id, request.url.path)
    if start_page:
        headers_out["accept-encoding"] = "identity"  # we edit this page (see ide.inject_defaults)
    upstream = client.build_request(request.method, url, headers=headers_out, content=request.stream())
    try:
        resp = await client.send(upstream, stream=True)
    except httpx.ConnectError:
        return _waiting_page(
            port,
            f"Nothing is answering on port {port} yet. Start your app in the terminal "
            f"(listen on 0.0.0.0:{port}). This page tries again every 2 seconds.",
        )
    except httpx.TimeoutException:
        return Response(f"Your app on port {port} took too long to answer.", status_code=504, media_type="text/plain")
    headers = {k: v for k, v in resp.headers.items() if k.lower() not in _HOP}
    location = headers.get("location")
    if location and location.startswith("/") and not location.startswith(prefix):
        headers["location"] = prefix + location  # keep redirects inside the preview
    await asyncio.to_thread(_touch, user, lab)
    if start_page and resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
        q = request.query_params  # lb_fs / lb_ts: the learner's editor and terminal text size (percent)
        page = ide.inject_defaults(
            (await resp.aread()).decode("utf-8", errors="replace"),
            ide.text_scale(q.get("lb_fs")), ide.text_scale(q.get("lb_ts")),
        )
        await resp.aclose()
        headers.pop("content-encoding", None)
        return Response(page, status_code=200, headers=headers, media_type="text/html")
    return StreamingResponse(resp.aiter_raw(), status_code=resp.status_code, headers=headers, background=BackgroundTask(resp.aclose))


def _waiting_page(port: int, message: str) -> Response:
    """A small page that reloads itself, so the preview appears as soon as the app starts."""
    html = (
        "<!doctype html><meta charset='utf-8'><meta http-equiv='refresh' content='2'>"
        "<title>Waiting for your app</title>"
        "<body style='font:15px/1.6 system-ui,sans-serif;margin:24px;color:#555e70'>"
        f"<p>{message}</p></body>"
    )
    return Response(html, status_code=502, media_type="text/html")


def _touch(user: User, lab: LabConfig) -> None:
    """Using the preview counts as activity for the idle reaper (throttled in touch())."""
    with Session(engine) as session:
        ws = containers.get_workspace(session, user, lab)
        containers.touch(session, ws, force=False)


async def proxy_ws(ws: WebSocket, lab_id: str, port: int, path: str, full_path: bool = False) -> None:
    try:
        user, lab, target = await asyncio.to_thread(_authorize, ws.cookies.get(COOKIE), lab_id, port, full_path)
    except HTTPException as e:
        await ws.close(code=4403 if e.status_code == 403 else 4404, reason=str(e.detail)[:120])
        return
    url = (f"ws://{target}{quote(ws.url.path)}" if full_path else f"ws://{target}/{quote(path)}") + (f"?{ws.url.query}" if ws.url.query else "")
    # The app's own cookies (VS Code keeps its connection token in one), never ours.
    cookies = [c for c in ws.headers.get("cookie", "").split(";") if c.strip() and not c.strip().startswith(COOKIE + "=")]
    try:
        upstream = await websockets.connect(
            url, open_timeout=5, max_size=None if full_path else 2**22,
            additional_headers={"cookie": ";".join(cookies)} if cookies else None,
        )
    except (OSError, websockets.WebSocketException, asyncio.TimeoutError):
        await ws.close(code=1011, reason=f"Nothing is answering on port {port}")
        return
    await ws.accept()

    last_touch = 0.0

    async def to_upstream() -> None:
        nonlocal last_touch
        while True:
            msg = await ws.receive()
            if msg["type"] == "websocket.disconnect":
                return
            data = msg["bytes"] if msg.get("bytes") is not None else msg.get("text", "")
            # Typing in VS Code (or a preview app) is activity for the idle reaper. Tiny messages are
            # keep-alives that an abandoned tab also sends, so they do not count.
            now = asyncio.get_running_loop().time()
            if len(data) >= ACTIVITY_MIN_BYTES and now - last_touch > ACTIVITY_EVERY_SECONDS:
                last_touch = now
                asyncio.get_running_loop().run_in_executor(None, _touch, user, lab)
            await upstream.send(data)

    async def to_browser() -> None:
        async for data in upstream:
            if isinstance(data, bytes):
                await ws.send_bytes(data)
            else:
                await ws.send_text(data)

    tasks = [asyncio.create_task(to_upstream()), asyncio.create_task(to_browser())]
    try:
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    finally:
        for t in tasks:
            t.cancel()
        await upstream.close()
        try:
            await ws.close()
        except RuntimeError:
            pass
