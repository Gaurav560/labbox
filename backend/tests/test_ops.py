"""Phase H6: metrics, request ids, JSON logs, health, Sentry switched off by default."""
import json
import logging
import os
import random
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import metrics, observability
from app.config import get_settings

LINE = re.compile(r'^[a-z_:][a-z0-9_:]*(\{([a-z_]+="([^"\\]|\\.)*",?)*\})? -?[0-9.e+Inf-]+$')


@pytest.fixture
def api(monkeypatch) -> TestClient:
    monkeypatch.setenv("METRICS_TOKEN", "test-metrics-token")
    get_settings.cache_clear()
    metrics.reset_for_tests()
    from app.main import app

    with TestClient(app) as c:
        yield c
    get_settings.cache_clear()


def scrape(api: TestClient) -> str:
    r = api.get("/metrics", headers={"Authorization": "Bearer test-metrics-token"})
    assert r.status_code == 200, r.text
    return r.text


def test_metrics_are_private(api):
    assert api.get("/metrics").status_code == 404  # not this machine, no token
    assert api.get("/metrics", headers={"Authorization": "Bearer wrong"}).status_code == 404
    assert metrics.allowed("127.0.0.1", None) and metrics.allowed("::1", None)


def test_metrics_count_requests_logins_and_checks(api):
    name = f"ops{random.randint(0, 10**8)}"
    token = api.post("/api/auth/signup", json={"username": name, "password": "secret123"}).json()["token"]
    api.post("/api/auth/login", json={"username": name, "password": "wrong-one"})
    api.post("/api/auth/login", json={"username": name, "password": "secret123"})
    api.get("/api/labs/no-such-lab", headers={"Authorization": f"Bearer {token}"})
    text = scrape(api)
    for line in text.splitlines():
        assert line.startswith("#") or LINE.match(line), line  # valid Prometheus text
    assert "labbox_up 1" in text
    assert "labbox_signups_total 1" in text
    assert 'labbox_logins_total{result="ok"} 1' in text and 'labbox_logins_total{result="wrong"} 1' in text
    # Route templates, never raw paths (a lab id in a label would grow without end).
    assert 'route="/api/labs/{lab_id}"' in text and "no-such-lab" not in text
    assert 'labbox_http_request_duration_seconds_bucket{route="/api/auth/signup",le="+Inf"} 1' in text
    assert re.search(r"labbox_learners_total \d+", text)


def test_histograms_are_cumulative():
    metrics.reset_for_tests()
    for s in (0.01, 0.2, 0.2, 3):
        metrics.observe("labbox_http_request_duration_seconds", s, route="/x")
    lines = {ln.split(" ")[0]: float(ln.split(" ")[1]) for ln in metrics._histogram_lines("labbox_http_request_duration_seconds", metrics.DURATION_BUCKETS)}
    assert lines['labbox_http_request_duration_seconds_bucket{route="/x",le="0.05"}'] == 1
    assert lines['labbox_http_request_duration_seconds_bucket{route="/x",le="0.25"}'] == 3
    assert lines['labbox_http_request_duration_seconds_bucket{route="/x",le="+Inf"}'] == 4
    assert lines['labbox_http_request_duration_seconds_count{route="/x"}'] == 4
    assert abs(lines['labbox_http_request_duration_seconds_sum{route="/x"}'] - 3.41) < 1e-9


def test_request_ids_come_back(api):
    r = api.get("/api/catalog")
    assert re.fullmatch(r"[0-9a-f]{16}", r.headers["x-request-id"])
    r = api.get("/api/catalog", headers={"X-Request-ID": "abc-123"})
    assert r.headers["x-request-id"] == "abc-123"  # a proxy's id is kept, so logs line up
    r = api.get("/api/catalog", headers={"X-Request-ID": "bad id with spaces"})
    assert r.headers["x-request-id"] != "bad id with spaces"


def test_json_logs_carry_the_request_id():
    record = logging.LogRecord("labbox.test", logging.WARNING, __file__, 1, "machine %s stopped", ("lab-u1-x",), None)
    token = observability.request_id.set("req-42")
    try:
        observability._RequestIdFilter().filter(record)
    finally:
        observability.request_id.reset(token)
    out = json.loads(observability.JsonFormatter().format(record))
    assert out["message"] == "machine lab-u1-x stopped" and out["level"] == "WARNING"
    assert out["request_id"] == "req-42" and out["logger"] == "labbox.test"


def test_health_reports_each_part(api):
    h = api.get("/api/health").json()
    assert h["ok"] is True and h["database"] is True and h["shared_state"] is True


def test_sentry_is_off_without_a_dsn():
    assert get_settings().SENTRY_DSN == ""
    assert observability.setup_sentry() is False


@pytest.mark.skipif(not os.environ.get("LABBOX_TEST_REDIS_URL"), reason="needs Redis (LABBOX_TEST_REDIS_URL)")
def test_counts_from_every_worker_add_up():
    metrics.reset_for_tests()
    metrics.count("labbox_signups_total")
    subprocess.run([sys.executable, "-c", "from app import metrics; metrics.count('labbox_signups_total', 2)"],
                   cwd=Path(__file__).resolve().parents[1], env={**os.environ, "REDIS_URL": os.environ["LABBOX_TEST_REDIS_URL"]}, check=True)
    assert "labbox_signups_total 3" in metrics._counter_lines("labbox_signups_total")
