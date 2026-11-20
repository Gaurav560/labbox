"""Logs, request ids and error reports (Phase H6).

- Every request gets an id (the X-Request-ID it came with, or a new one), sent back in the response and
  added to every log line written while serving it, so one learner's problem can be followed in the logs.
- LOG_FORMAT=json writes one JSON object a line (time, level, logger, message, request_id, error).
- Requests that fail (5xx) or are slow (over 2 s) are logged as warnings with route, status and time.
- SENTRY_DSN turns on error reports to Sentry; without it nothing is sent anywhere. Reports carry no
  personal data (no cookies, headers, request bodies or IP addresses).
"""
import contextvars
import json
import logging
import secrets
import time
from collections import deque
from datetime import datetime, timezone

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from . import metrics, shared
from .config import get_settings

request_id: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")
SLOW_SECONDS = 2.0
log = logging.getLogger("labbox.http")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        out = {
            "time": datetime.fromtimestamp(record.created, timezone.utc).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if getattr(record, "request_id", ""):
            out["request_id"] = record.request_id
        if record.exc_info:
            out["error"] = self.formatException(record.exc_info)
        return json.dumps(out, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(_RequestIdFilter())
    if get_settings().LOG_FORMAT.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)


def setup_sentry() -> bool:
    dsn = get_settings().SENTRY_DSN
    if not dsn:
        return False
    import sentry_sdk

    def scrub(event, hint):
        req = event.get("request") or {}
        for k in ("cookies", "headers", "data", "env"):
            req.pop(k, None)
        event.pop("user", None)
        return event

    sentry_sdk.init(dsn=dsn, environment=get_settings().SENTRY_ENVIRONMENT, send_default_pii=False,
                    traces_sample_rate=0, before_send=scrub)
    logging.getLogger("labbox").info("Sentry error reports are on (%s)", get_settings().SENTRY_ENVIRONMENT)
    return True


RECENT_ERRORS = 200
_errors: deque[str] = deque(maxlen=RECENT_ERRORS)


def remember_error(method: str, route: str, status: int, rid: str, ms: int, error: str) -> None:
    """The latest server errors, for the admin page (Phase J); shared by every worker through Redis."""
    item = json.dumps({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "method": method, "route": route,
                       "status": status, "request_id": rid, "ms": ms, "error": error})
    try:
        r = shared.redis_client()
        if r is None:
            _errors.appendleft(item)
            return
        p = r.pipeline(transaction=False)
        p.lpush(shared.PREFIX + "errors", item)
        p.ltrim(shared.PREFIX + "errors", 0, RECENT_ERRORS - 1)
        p.execute()
    except Exception:
        pass


def recent_errors(limit: int = 100) -> list[dict]:
    r = shared.redis_client()
    raw = list(_errors)[:limit] if r is None else r.lrange(shared.PREFIX + "errors", 0, limit - 1)
    return [json.loads(x) for x in raw]


def _route(scope: Scope) -> str:
    """The route template (/api/labs/{lab_id}/check), never the raw path: metric labels stay few."""
    route = scope.get("route")
    return getattr(route, "path", None) or "unmatched"


class RequestMiddleware:
    """Request id, metrics and slow/failed request logs for every HTTP request (pure ASGI, so
    streaming responses and websockets pass straight through)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope.get("headers") or []).get(b"x-request-id", b"").decode(errors="ignore")
        rid = incoming[:64] if incoming and incoming.replace("-", "").isalnum() else secrets.token_hex(8)
        token = request_id.set(rid)
        started = time.monotonic()
        status = 500

        async def send_wrapped(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                message.setdefault("headers", [])
                message["headers"] = [*message["headers"], (b"x-request-id", rid.encode())]
            await send(message)

        error = ""
        try:
            await self.app(scope, receive, send_wrapped)
        except Exception as e:
            error = f"{type(e).__name__}: {e}"[:300]
            raise
        finally:
            took = time.monotonic() - started
            route = _route(scope)
            if route != "/metrics":
                metrics.count("labbox_http_requests_total", method=scope.get("method", ""), route=route, status=str(status))
                metrics.observe("labbox_http_request_duration_seconds", took, route=route)
            if status >= 500 or took > SLOW_SECONDS:
                log.warning("%s %s -> %s in %d ms", scope.get("method"), route, status, int(took * 1000))
            if status >= 500:
                remember_error(scope.get("method", ""), route, status, rid, int(took * 1000), error)
            request_id.reset(token)
