"""The LLM gateway (Phase E) with the fake provider: aliases, lab tokens, budgets, logging, the
OpenAI and Anthropic shapes, streaming, and `lab requests`. No Docker, no real models."""
import json
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import llm_gateway, shared
from app.auth import create_scoped_token, create_token
from app.config import get_settings
from app.db import engine, init_db
from app.llm_gateway import create_lab_token, gateway_app
from app.models import LlmRequest, User


@pytest.fixture
def user() -> User:
    init_db()
    with Session(engine) as s:
        u = User(username=f"llm{uuid.uuid4().hex[:8]}", password_hash="x")
        s.add(u)
        s.commit()
        s.refresh(u)
    shared.forget_hits()
    return u


@pytest.fixture
def gw() -> TestClient:
    return TestClient(gateway_app)


def auth(u: User, lab: str = "ai-lab") -> dict[str, str]:
    return {"Authorization": f"Bearer {create_lab_token(u.id, lab)}"}


def rows(u: User) -> list[LlmRequest]:
    with Session(engine) as s:
        return list(s.exec(select(LlmRequest).where(LlmRequest.user_id == u.id).order_by(LlmRequest.id)).all())


def test_chat_with_an_alias_is_logged(gw: TestClient, user: User):
    r = gw.post("/llm/v1/chat/completions", headers=auth(user), json={"model": "lab-chat", "messages": [{"role": "user", "content": "hello there"}]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["model"] == "lab-chat"  # the learner sees the alias, never the vendor model
    assert body["choices"][0]["message"]["content"] == "Fake reply to: hello there"
    [row] = rows(user)
    assert (row.lab_id, row.endpoint, row.alias, row.model, row.status) == ("ai-lab", "chat", "lab-chat", "fake/chat-small", 200)
    assert row.prompt_tokens > 0 and row.completion_tokens > 0
    assert json.loads(row.request_json)["max_tokens"] == get_settings().LLM_MAX_TOKENS  # capped even when not asked


def test_bad_keys_and_unknown_models(gw: TestClient, user: User):
    body = {"model": "lab-chat", "messages": [{"role": "user", "content": "hi"}]}
    assert gw.post("/llm/v1/chat/completions", json=body).status_code == 401
    assert gw.post("/llm/v1/chat/completions", headers={"Authorization": "Bearer nonsense"}, json=body).status_code == 401
    # A login token or a preview token is not an LLM key.
    for token in (create_token(user), create_scoped_token(user, "preview", 5)):
        r = gw.post("/llm/v1/chat/completions", headers={"Authorization": f"Bearer {token}"}, json=body)
        assert r.status_code == 401 and r.json()["error"]["code"] == "invalid_api_key"
    r = gw.post("/llm/v1/chat/completions", headers=auth(user), json={**body, "model": "gpt-4o"})
    assert r.status_code == 400 and "lab-chat" in r.json()["error"]["message"]
    assert rows(user) == []


def test_max_tokens_is_capped(gw: TestClient, user: User):
    gw.post("/llm/v1/chat/completions", headers=auth(user), json={"model": "lab-chat", "max_tokens": 10**6, "messages": [{"role": "user", "content": "x"}]})
    assert json.loads(rows(user)[0].request_json)["max_tokens"] == get_settings().LLM_MAX_TOKENS


def test_daily_budget_gives_a_clear_429(gw: TestClient, user: User, monkeypatch):
    monkeypatch.setattr(get_settings(), "LLM_DAILY_TOKENS", 30)
    body = {"model": "lab-chat", "messages": [{"role": "user", "content": "tell me a long story " * 20}]}
    assert gw.post("/llm/v1/chat/completions", headers=auth(user), json=body).status_code == 200
    r = gw.post("/llm/v1/chat/completions", headers=auth(user), json=body)
    assert r.status_code == 429
    err = r.json()["error"]
    assert err["code"] == "budget_exceeded" and "resets at midnight UTC" in err["message"]


def test_requests_per_minute(gw: TestClient, user: User, monkeypatch):
    monkeypatch.setattr(get_settings(), "LLM_RPM", 2)
    body = {"model": "lab-chat", "messages": [{"role": "user", "content": "hi"}]}
    codes = [gw.post("/llm/v1/chat/completions", headers=auth(user), json=body).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_embeddings(gw: TestClient, user: User):
    r = gw.post("/llm/v1/embeddings", headers=auth(user), json={"model": "lab-embed", "input": ["filter coffee", "cold coffee"]})
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data) == 2 and len(data[0]["embedding"]) == 16 and data[0]["embedding"] != data[1]["embedding"]
    assert rows(user)[0].endpoint == "embeddings"


def test_streaming_relays_chunks_and_logs_usage(gw: TestClient, user: User):
    body = {"model": "lab-chat", "stream": True, "messages": [{"role": "user", "content": "stream please"}]}
    with gw.stream("POST", "/llm/v1/chat/completions", headers=auth(user), json=body) as r:
        assert r.status_code == 200
        events = [line for line in r.iter_lines() if line.startswith("data: ")]
    assert events[-1] == "data: [DONE]"
    chunks = [json.loads(e[6:]) for e in events[:-1]]
    assert "".join((c["choices"][0]["delta"].get("content") or "") for c in chunks if c["choices"]) == "Fake reply to: stream please"
    assert all(c["model"] == "lab-chat" for c in chunks)
    [row] = rows(user)
    assert row.response_json.strip('"') == "Fake reply to: stream please" and row.completion_tokens > 0


def test_anthropic_messages_shape(gw: TestClient, user: User):
    headers = {"x-api-key": create_lab_token(user.id, "ai-lab"), "anthropic-version": "2023-06-01"}
    r = gw.post("/llm/anthropic/v1/messages", headers=headers, json={
        "model": "lab-chat", "max_tokens": 100, "system": "Be brief.",
        "messages": [{"role": "user", "content": [{"type": "text", "text": "hi from anthropic"}]}],
    })
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["type"] == "message" and out["content"][0]["text"] == "Fake reply to: hi from anthropic"
    assert out["usage"]["input_tokens"] > 0 and out["stop_reason"] == "end_turn"
    sent = json.loads(rows(user)[0].request_json)
    assert sent["messages"][0] == {"role": "system", "content": "Be brief."}


def test_lab_requests_table_and_last(gw: TestClient, user: User):
    for text in ("first", "second"):
        gw.post("/llm/v1/chat/completions", headers=auth(user), json={"model": "lab-chat", "messages": [{"role": "user", "content": text}]})
    table = gw.get("/llm/requests", headers=auth(user)).text
    assert table.count("lab-chat") == 2 and "Tokens used today" in table
    last = gw.get("/llm/requests?last=true", headers=auth(user)).text
    assert "second" in last and "--- response ---" in last


def test_upstream_down_is_a_502_and_logged(gw: TestClient, user: User, monkeypatch):
    monkeypatch.setattr(get_settings(), "LLM_MODELS", "lab-chat=ollama/tiny")
    monkeypatch.setattr(get_settings(), "OLLAMA_URL", "http://127.0.0.1:9")  # nothing listens there
    r = gw.post("/llm/v1/chat/completions", headers=auth(user), json={"model": "lab-chat", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 502 and "scripts/ollama.sh" in r.json()["error"]["message"]
    assert rows(user)[0].status == 502


def test_paid_provider_without_key_is_refused(gw: TestClient, user: User, monkeypatch):
    monkeypatch.setattr(get_settings(), "LLM_MODELS", "lab-chat=openai/gpt-4o-mini")
    monkeypatch.setattr(get_settings(), "OPENAI_API_KEY", "")
    r = gw.post("/llm/v1/chat/completions", headers=auth(user), json={"model": "lab-chat", "messages": [{"role": "user", "content": "hi"}]})
    assert r.status_code == 503 and r.json()["error"]["code"] == "provider_not_configured"


def test_model_aliases_parse():
    s = get_settings()
    assert s.llm_models["lab-chat"] == ("fake", "chat-small")
    assert llm_gateway.cost_usd("openai", "gpt-4o-mini", 1_000_000, 1_000_000) == 0.75
