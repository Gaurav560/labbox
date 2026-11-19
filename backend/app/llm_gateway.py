"""The LLM gateway (v2 spec 6.1): one safe door from lab code to language models.

Labs call model aliases (lab-chat, lab-chat-smart, lab-embed) with an OpenAI- or Anthropic-style
request and a per-user lab token. The gateway maps the alias to a real provider and model, enforces
the user's budget, logs every call, and keeps the real provider keys on the server.

It is its own small FastAPI app, served on a separate port (LLM_GATEWAY_PORT) so lab containers can
reach it through a relay without reaching the main API.
"""
import asyncio
import hashlib
import json
import logging
import math
import time
from collections import defaultdict, deque
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from jose import JWTError, jwt
from sqlalchemy import func
from sqlmodel import Session, col, select

from .config import get_settings
from .db import engine
from .models import LlmRequest, User, utcnow

log = logging.getLogger(__name__)

ALGORITHM = "HS256"
TOKEN_SCOPE = "llm"
TOKEN_DAYS = 30
LOG_CAP = 20_000  # characters of request and response kept per call
# USD per million tokens (input, output). Local and fake models are free; unknown models count as 0.
PRICES: dict[str, tuple[float, float]] = {
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4.1-mini": (0.40, 1.60),
    "openai/text-embedding-3-small": (0.02, 0.0),
    "gemini/gemini-2.0-flash": (0.10, 0.40),
}
UPSTREAMS = {  # OpenAI-compatible base URLs and the setting holding each key
    "openai": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY"),
}


class GatewayError(Exception):
    """Becomes an OpenAI-shaped error response: {"error": {"message", "type", "code"}}."""

    def __init__(self, status: int, message: str, code: str, kind: str = "invalid_request_error"):
        super().__init__(message)
        self.status, self.message, self.code, self.kind = status, message, code, kind


# ---------- lab tokens ----------


def create_lab_token(user_id: int, lab_id: str) -> str:
    """The OPENAI_API_KEY a lab container gets: only valid at the gateway, for one user and lab."""
    exp = datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS)
    return jwt.encode({"sub": str(user_id), "scope": TOKEN_SCOPE, "lab": lab_id, "exp": exp}, get_settings().JWT_SECRET, algorithm=ALGORITHM)


class Identity:
    def __init__(self, user_id: int, lab_id: str):
        self.user_id, self.lab_id = user_id, lab_id


def identity_from_token(token: str) -> Identity | None:
    try:
        p = jwt.decode(token, get_settings().JWT_SECRET, algorithms=[ALGORITHM])
        if p.get("scope") != TOKEN_SCOPE:
            return None  # a login or preview token is never an LLM key, and the other way round
        return Identity(int(p["sub"]), str(p["lab"]))
    except (JWTError, KeyError, ValueError, TypeError):
        return None


def _token_from_request(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.headers.get("x-api-key", "").strip()  # the Anthropic SDK sends its key here


def require_identity(request: Request) -> Identity:
    ident = identity_from_token(_token_from_request(request))
    if ident is None:
        raise GatewayError(401, "Invalid lab key. Use the OPENAI_API_KEY (or ANTHROPIC_API_KEY) your lab machine was given.", "invalid_api_key", "authentication_error")
    with Session(engine) as s:
        if s.get(User, ident.user_id) is None:
            raise GatewayError(401, "This lab key belongs to a user that no longer exists.", "invalid_api_key", "authentication_error")
    return ident


# ---------- budgets ----------

_recent: dict[int, deque[float]] = defaultdict(deque)  # user id -> request times (this process)


def tokens_used_today(user_id: int) -> int:
    start = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    with Session(engine) as s:
        q = select(func.coalesce(func.sum(LlmRequest.prompt_tokens + LlmRequest.completion_tokens), 0)).where(
            LlmRequest.user_id == user_id, col(LlmRequest.created_at) >= start
        )
        return int(s.exec(q).one())


def check_budget(user_id: int) -> None:
    settings = get_settings()
    now = time.monotonic()
    times = _recent[user_id]
    while times and now - times[0] > 60:
        times.popleft()
    if len(times) >= settings.LLM_RPM:
        raise GatewayError(429, f"Too many requests: the limit is {settings.LLM_RPM} a minute. Wait a few seconds and try again.", "rate_limited", "rate_limit_error")
    used = tokens_used_today(user_id)
    if used >= settings.LLM_DAILY_TOKENS:
        raise GatewayError(
            429,
            f"Your AI budget for today is used up ({used:,} of {settings.LLM_DAILY_TOKENS:,} tokens). It resets at midnight UTC.",
            "budget_exceeded",
            "rate_limit_error",
        )
    times.append(now)


def cap_max_tokens(body: dict[str, Any]) -> None:
    cap = get_settings().LLM_MAX_TOKENS
    for key in ("max_tokens", "max_completion_tokens"):
        if isinstance(body.get(key), int):
            body[key] = max(1, min(body[key], cap))
    if not any(k in body for k in ("max_tokens", "max_completion_tokens")):
        body["max_tokens"] = cap


# ---------- providers ----------


def resolve(alias: Any) -> tuple[str, str]:
    models = get_settings().llm_models
    if alias not in models:
        names = ", ".join(sorted(models)) or "none configured"
        raise GatewayError(400, f"Unknown model {alias!r}. Labs use model aliases: {names}.", "model_not_found")
    return models[alias]


def _base_and_key(provider: str) -> tuple[str, str]:
    settings = get_settings()
    if provider == "ollama":
        return settings.OLLAMA_URL.rstrip("/") + "/v1", "ollama"
    if provider in UPSTREAMS:
        base, key_name = UPSTREAMS[provider]
        key = getattr(settings, key_name, "")
        if not key:
            raise GatewayError(503, f"The {provider} provider has no key on the server.", "provider_not_configured", "server_error")
        return base, key
    raise GatewayError(503, f"Unknown provider {provider!r} in LLM_MODELS.", "provider_not_configured", "server_error")


def _fake_tokens(text: str) -> int:
    return max(1, math.ceil(len(text) / 4))


def fake_chat_reply(messages: list[dict[str, Any]]) -> str:
    """The fake provider's answer (tests replace this to script a model)."""
    last = next((m for m in reversed(messages) if m.get("role") == "user"), {"content": ""})
    content = last.get("content")
    text = content if isinstance(content, str) else " ".join(p.get("text", "") for p in content or [] if isinstance(p, dict))
    return f"Fake reply to: {text[:80]}"


def _fake_chat(model: str, body: dict[str, Any]) -> dict[str, Any]:
    messages = body.get("messages") or []
    reply = fake_chat_reply(messages)
    prompt = _fake_tokens(json.dumps(messages))
    completion = min(_fake_tokens(reply), body.get("max_tokens") or 10**6)
    return {
        "id": "chatcmpl-fake",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": prompt + completion},
    }


def _fake_embed(inputs: list[str]) -> dict[str, Any]:
    data = []
    for i, text in enumerate(inputs):
        digest = hashlib.sha256(text.encode()).digest()
        vec = [b / 255 - 0.5 for b in digest[:16]]
        norm = math.sqrt(sum(v * v for v in vec)) or 1
        data.append({"object": "embedding", "index": i, "embedding": [v / norm for v in vec]})
    tokens = sum(_fake_tokens(t) for t in inputs)
    return {"object": "list", "data": data, "model": "fake", "usage": {"prompt_tokens": tokens, "total_tokens": tokens}}


async def upstream_post(provider: str, model: str, path: str, body: dict[str, Any]) -> dict[str, Any]:
    if provider == "fake":
        if path == "/chat/completions":
            return _fake_chat(model, body)
        inputs = body.get("input")
        return _fake_embed([inputs] if isinstance(inputs, str) else list(inputs or []))
    base, key = _base_and_key(provider)
    payload = {**body, "model": model}
    try:
        async with httpx.AsyncClient(timeout=get_settings().LLM_TIMEOUT_SECONDS) as client:
            r = await client.post(base + path, json=payload, headers={"Authorization": f"Bearer {key}"})
    except httpx.HTTPError as e:
        hint = " Is Ollama running? Start it with scripts/ollama.sh." if provider == "ollama" else ""
        raise GatewayError(502, f"Could not reach the model provider ({type(e).__name__}).{hint}", "upstream_unreachable", "server_error")
    if r.status_code >= 400:
        try:
            msg = r.json().get("error", {})
            msg = msg.get("message") if isinstance(msg, dict) else msg
        except ValueError:
            msg = r.text[:300]
        raise GatewayError(502 if r.status_code >= 500 else 400, f"The model provider said: {msg}", "upstream_error", "api_error")
    return r.json()


async def upstream_stream(provider: str, model: str, body: dict[str, Any]) -> AsyncIterator[bytes]:
    """Yields the provider's SSE bytes as they arrive (fake: one chunk, then the usage, then [DONE])."""
    if provider == "fake":
        full = _fake_chat(model, body)
        text = full["choices"][0]["message"]["content"]
        base = {"id": "chatcmpl-fake", "object": "chat.completion.chunk", "created": full["created"], "model": model}
        yield f"data: {json.dumps({**base, 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': text}, 'finish_reason': None}]})}\n\n".encode()
        yield f"data: {json.dumps({**base, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n".encode()
        yield f"data: {json.dumps({**base, 'choices': [], 'usage': full['usage']})}\n\n".encode()
        yield b"data: [DONE]\n\n"
        return
    base_url, key = _base_and_key(provider)
    payload = {**body, "model": model, "stream": True, "stream_options": {"include_usage": True}}
    async with httpx.AsyncClient(timeout=get_settings().LLM_TIMEOUT_SECONDS) as client:
        async with client.stream("POST", base_url + "/chat/completions", json=payload, headers={"Authorization": f"Bearer {key}"}) as r:
            if r.status_code >= 400:
                raise GatewayError(502, f"The model provider said: {(await r.aread()).decode(errors='replace')[:300]}", "upstream_error", "api_error")
            async for chunk in r.aiter_bytes():
                yield chunk


# ---------- logging ----------


def cost_usd(provider: str, model: str, prompt: int, completion: int) -> float:
    pin, pout = PRICES.get(f"{provider}/{model}", (0.0, 0.0))
    return round((prompt * pin + completion * pout) / 1_000_000, 6)


def record(ident: Identity, endpoint: str, alias: str, target: tuple[str, str], started: float, request: Any,
           response: Any = None, usage: dict[str, Any] | None = None, status: int = 200, error: str | None = None) -> None:
    usage = usage or {}
    prompt = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
    completion = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
    row = LlmRequest(
        user_id=ident.user_id,
        lab_id=ident.lab_id,
        endpoint=endpoint,
        alias=str(alias),
        model=f"{target[0]}/{target[1]}",
        prompt_tokens=prompt,
        completion_tokens=completion,
        cost_usd=cost_usd(target[0], target[1], prompt, completion),
        latency_ms=int((time.monotonic() - started) * 1000),
        status=status,
        error=error,
        request_json=json.dumps(request, default=str)[:LOG_CAP],
        response_json=(response if isinstance(response, str) else json.dumps(response, default=str))[:LOG_CAP] if response is not None else "",
    )
    with Session(engine) as s:
        s.add(row)
        s.commit()


# ---------- the core calls (also used by the tutor) ----------


async def chat(ident: Identity, body: dict[str, Any], endpoint: str = "chat") -> dict[str, Any]:
    """A non-streaming chat completion with budget checks and logging. Raises GatewayError."""
    alias = body.get("model")
    target = resolve(alias)
    check_budget(ident.user_id)
    cap_max_tokens(body)
    started = time.monotonic()
    try:
        out = await upstream_post(*target, "/chat/completions", body)
    except GatewayError as e:
        record(ident, endpoint, alias, target, started, body, status=e.status, error=e.message)
        raise
    record(ident, endpoint, alias, target, started, body, out, out.get("usage"))
    return {**out, "model": alias}


async def embeddings(ident: Identity, body: dict[str, Any]) -> dict[str, Any]:
    alias = body.get("model")
    target = resolve(alias)
    check_budget(ident.user_id)
    started = time.monotonic()
    try:
        out = await upstream_post(*target, "/embeddings", body)
    except GatewayError as e:
        record(ident, "embeddings", alias, target, started, body, status=e.status, error=e.message)
        raise
    summary = {"data": f"{len(out.get('data', []))} vector(s)", "usage": out.get("usage")}
    record(ident, "embeddings", alias, target, started, body, summary, out.get("usage"))
    return {**out, "model": alias}


async def chat_stream(ident: Identity, body: dict[str, Any]) -> AsyncIterator[bytes]:
    alias = body.get("model")
    target = resolve(alias)
    check_budget(ident.user_id)
    cap_max_tokens(body)
    started = time.monotonic()
    text, usage, buffer = [], None, b""

    async def gen() -> AsyncIterator[bytes]:
        nonlocal usage, buffer
        try:
            async for chunk in upstream_stream(*target, body):
                buffer += chunk
                while b"\n\n" in buffer:  # parse whole SSE events to collect the text and the usage
                    event, buffer = buffer.split(b"\n\n", 1)
                    line = event.decode(errors="replace").strip()
                    if line.startswith("data:") and line != "data: [DONE]":
                        try:
                            data = json.loads(line[5:])
                        except ValueError:
                            continue
                        usage = data.get("usage") or usage
                        for ch in data.get("choices") or []:
                            text.append((ch.get("delta") or {}).get("content") or "")
                        data["model"] = alias
                        yield f"data: {json.dumps(data)}\n\n".encode()
                    elif line:
                        yield (line + "\n\n").encode()
        except GatewayError as e:
            record(ident, "chat", alias, target, started, body, status=e.status, error=e.message)
            yield f"data: {json.dumps({'error': {'message': e.message, 'type': e.kind, 'code': e.code}})}\n\n".encode()
            return
        record(ident, "chat", alias, target, started, body, "".join(text), usage)

    return gen()


# ---------- Anthropic Messages, translated to and from chat completions ----------


def _anthropic_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


async def messages(ident: Identity, body: dict[str, Any]) -> dict[str, Any]:
    if body.get("stream"):
        raise GatewayError(400, "Streaming is not supported on the Anthropic endpoint yet; use stream=False.", "stream_not_supported")
    chat_messages = []
    if body.get("system"):
        chat_messages.append({"role": "system", "content": _anthropic_text(body["system"])})
    for m in body.get("messages") or []:
        chat_messages.append({"role": m.get("role", "user"), "content": _anthropic_text(m.get("content"))})
    req = {"model": body.get("model"), "messages": chat_messages, "max_tokens": body.get("max_tokens") or get_settings().LLM_MAX_TOKENS}
    for key in ("temperature", "top_p"):
        if key in body:
            req[key] = body[key]
    if body.get("stop_sequences"):
        req["stop"] = body["stop_sequences"]
    out = await chat(ident, req, endpoint="messages")
    choice = (out.get("choices") or [{}])[0]
    usage = out.get("usage") or {}
    return {
        "id": "msg_" + str(out.get("id", "lab"))[-24:],
        "type": "message",
        "role": "assistant",
        "model": body.get("model"),
        "content": [{"type": "text", "text": (choice.get("message") or {}).get("content") or ""}],
        "stop_reason": "max_tokens" if choice.get("finish_reason") == "length" else "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": usage.get("prompt_tokens", 0), "output_tokens": usage.get("completion_tokens", 0)},
    }


# ---------- request history (`lab requests`) ----------


def recent(ident: Identity, limit: int = 10) -> list[LlmRequest]:
    with Session(engine) as s:
        q = select(LlmRequest).where(LlmRequest.user_id == ident.user_id).order_by(col(LlmRequest.id).desc()).limit(limit)
        return list(s.exec(q).all())


def requests_table(rows: list[LlmRequest], used: int) -> str:
    settings = get_settings()
    lines = [f"{'time (UTC)':19}  {'model':15} {'kind':10} {'in':>6} {'out':>6} {'ms':>6}  {'cost $':>9}  status"]
    for r in reversed(rows):
        status = "ok" if r.status == 200 else f"{r.status} {(r.error or '')[:40]}"
        lines.append(f"{r.created_at:%Y-%m-%d %H:%M:%S}  {r.alias[:15]:15} {r.endpoint[:10]:10} {r.prompt_tokens:>6} {r.completion_tokens:>6} {r.latency_ms:>6}  {r.cost_usd:>9.6f}  {status}")
    if not rows:
        lines.append("(no requests yet)")
    lines.append(f"\nTokens used today: {used:,} of {settings.LLM_DAILY_TOKENS:,}. `lab requests --last` shows the full last request.")
    return "\n".join(lines) + "\n"


# ---------- the app ----------

gateway_app = FastAPI(title="LabBox LLM gateway", docs_url=None, redoc_url=None, openapi_url=None)


@gateway_app.exception_handler(GatewayError)
async def _gateway_error(_: Request, e: GatewayError) -> JSONResponse:
    return JSONResponse({"error": {"message": e.message, "type": e.kind, "code": e.code}}, status_code=e.status)


async def _json_body(request: Request) -> dict[str, Any]:
    try:
        body = await request.json()
    except ValueError:
        raise GatewayError(400, "The request body must be JSON.", "invalid_json")
    if not isinstance(body, dict):
        raise GatewayError(400, "The request body must be a JSON object.", "invalid_json")
    return body


@gateway_app.get("/llm/health")
async def health() -> dict[str, Any]:
    return {"ok": True, "models": sorted(get_settings().llm_models)}


@gateway_app.get("/llm/v1/models")
async def list_models(ident: Identity = Depends(require_identity)) -> dict[str, Any]:
    return {"object": "list", "data": [{"id": a, "object": "model", "owned_by": "labbox"} for a in sorted(get_settings().llm_models)]}


@gateway_app.post("/llm/v1/chat/completions")
async def chat_completions(request: Request, ident: Identity = Depends(require_identity)):
    body = await _json_body(request)
    if body.get("stream"):
        body.pop("stream", None)
        body.pop("stream_options", None)
        return StreamingResponse(await chat_stream(ident, body), media_type="text/event-stream")
    return await chat(ident, body)


@gateway_app.post("/llm/v1/embeddings")
async def create_embeddings(request: Request, ident: Identity = Depends(require_identity)):
    return await embeddings(ident, await _json_body(request))


@gateway_app.post("/llm/anthropic/v1/messages")
async def anthropic_messages(request: Request, ident: Identity = Depends(require_identity)):
    return await messages(ident, await _json_body(request))


@gateway_app.get("/llm/requests")
async def my_requests(format: str = "text", last: bool = False, ident: Identity = Depends(require_identity)):
    rows = await asyncio.to_thread(recent, ident, 1 if last else 10)
    if last:
        if not rows:
            return PlainTextResponse("(no requests yet)\n")
        r = rows[0]
        return PlainTextResponse(f"{r.created_at:%Y-%m-%d %H:%M:%S} UTC  {r.alias} -> {r.model}  {r.prompt_tokens} in, {r.completion_tokens} out\n\n"
                                 f"--- request ---\n{r.request_json}\n\n--- response ---\n{r.response_json or r.error or ''}\n")
    if format == "json":
        return [r.model_dump(exclude={"user_id", "request_json", "response_json"}, mode="json") for r in rows]
    used = await asyncio.to_thread(tokens_used_today, ident.user_id)
    return PlainTextResponse(requests_table(rows, used))


# ---------- serving it next to the main API ----------


def bind_host() -> str:
    """Where the gateway listens: LLM_GATEWAY_HOST, else the Docker bridge address (reachable by the lab
    relays, not by the outside world), else localhost."""
    host = get_settings().LLM_GATEWAY_HOST
    if host:
        return host
    try:
        from . import containers

        cfg = containers.client().networks.get("bridge").attrs["IPAM"]["Config"]
        return next(c["Gateway"] for c in cfg if c.get("Gateway"))
    except Exception:
        return "127.0.0.1"


async def serve() -> None:
    import uvicorn

    settings = get_settings()
    host = await asyncio.to_thread(bind_host)
    config = uvicorn.Config(gateway_app, host=host, port=settings.LLM_GATEWAY_PORT, log_level="warning", lifespan="off")
    log.info("LLM gateway on http://%s:%d (models: %s)", host, settings.LLM_GATEWAY_PORT, ", ".join(sorted(settings.llm_models)))
    try:
        await uvicorn.Server(config).serve()
    except (OSError, SystemExit) as e:  # port taken: the main API keeps running without the gateway
        log.error("LLM gateway could not start on %s:%d: %s", host, settings.LLM_GATEWAY_PORT, e)
