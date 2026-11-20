"""Metrics for Prometheus (Phase H6), served at GET /metrics in Prometheus' text format.

Counters and histograms are kept in Redis (in memory without REDIS_URL), so the numbers add up across
every uvicorn worker. Gauges (machines running, active learners, background jobs) are read at the
moment Prometheus asks. No extra library: the text format is simple.

/metrics answers only the machine itself (Prometheus on the same server) or a request carrying
METRICS_TOKEN; nginx never passes it on, and the Vite dev proxy only forwards /api.
"""
import threading
from collections import defaultdict
from datetime import timedelta

from sqlalchemy import func
from sqlmodel import Session, select

from . import containers, shared
from .config import get_settings
from .db import engine
from .models import User, Workspace, utcnow

DURATION_BUCKETS = (0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30)
CHECK_BUCKETS = (0.5, 1, 2, 5, 10, 20, 30, 60, 120)

HELP = {
    "labbox_http_requests_total": ("counter", "HTTP requests by method, route template and status."),
    "labbox_http_request_duration_seconds": ("histogram", "HTTP request time by route template."),
    "labbox_checks_total": ("counter", "Checks by result: passed (every task), failed, error."),
    "labbox_check_duration_seconds": ("histogram", "Time a check takes, end to end."),
    "labbox_machines_stopped_total": ("counter", "Lab machines stopped by the platform, by reason."),
    "labbox_logins_total": ("counter", "Login attempts by result: ok, wrong, limited."),
    "labbox_signups_total": ("counter", "New accounts."),
    "labbox_rate_limited_total": ("counter", "Requests refused by a rate limit, by limit."),
    "labbox_ai_requests_total": ("counter", "AI gateway requests by model alias and status."),
    "labbox_machines_running": ("gauge", "Lab machines running now."),
    "labbox_learners_total": ("gauge", "Accounts."),
    "labbox_learners_active": ("gauge", "Learners with a lab in use, by window."),
    "labbox_job_last_run_timestamp_seconds": ("gauge", "When each background job last ran (Unix time)."),
    "labbox_job_last_ok": ("gauge", "1 if the background job's last run went well."),
    "labbox_up": ("gauge", "1 while the backend answers."),
}

_mem: defaultdict[str, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
_mem_guard = threading.Lock()


def _labels(labels: dict[str, str]) -> str:
    def esc(v: str) -> str:
        return str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")

    return ",".join(f'{k}="{esc(v)}"' for k, v in sorted(labels.items()))


def _add(name: str, fields: dict[str, float]) -> None:
    r = shared.redis_client()
    if r is None:
        with _mem_guard:
            for f, v in fields.items():
                _mem[name][f] += v
        return
    p = r.pipeline(transaction=False)
    for f, v in fields.items():
        p.hincrbyfloat(shared.PREFIX + "metrics:" + name, f, v)
    p.execute()


def _all(name: str) -> dict[str, float]:
    r = shared.redis_client()
    if r is None:
        with _mem_guard:
            return dict(_mem[name])
    raw = r.hgetall(shared.PREFIX + "metrics:" + name)
    return {(k.decode() if isinstance(k, bytes) else k): float(v) for k, v in raw.items()}


def count(name: str, amount: float = 1, **labels: str) -> None:
    """Add to a counter (fails quietly: metrics never break a request)."""
    try:
        _add(name, {_labels(labels): amount})
    except Exception:
        pass


def observe(name: str, seconds: float, buckets: tuple = DURATION_BUCKETS, **labels: str) -> None:
    """One observation for a histogram: its bucket, the sum and the count (cumulated when served)."""
    base = _labels(labels)
    le = next((str(b) for b in buckets if seconds <= b), "+Inf")
    try:
        _add(name, {f"{base}|le={le}": 1, f"{base}|sum": seconds, f"{base}|count": 1})
    except Exception:
        pass


def reset_for_tests() -> None:
    with _mem_guard:
        _mem.clear()
    r = shared.redis_client()
    if r is not None:
        for k in r.scan_iter(shared.PREFIX + "metrics:*"):
            r.delete(k)


# ---------- the text Prometheus reads ----------


def _num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else repr(float(v))


def _counter_lines(name: str) -> list[str]:
    return [f"{name}{{{lbl}}} {_num(v)}" if lbl else f"{name} {_num(v)}" for lbl, v in sorted(_all(name).items())]


def _histogram_lines(name: str, buckets: tuple) -> list[str]:
    series: defaultdict[str, dict[str, float]] = defaultdict(dict)
    for field, v in _all(name).items():
        base, _, part = field.rpartition("|")
        series[base][part] = v
    out = []
    for base, parts in sorted(series.items()):
        running = 0.0
        for b in [*map(str, buckets), "+Inf"]:
            running += parts.get(f"le={b}", 0)
            lbl = _labels({"le": b}) if not base else f'{base},le="{b}"'
            out.append(f"{name}_bucket{{{lbl}}} {_num(running)}")
        wrap = f"{{{base}}}" if base else ""
        out.append(f"{name}_sum{wrap} {_num(parts.get('sum', 0))}")
        out.append(f"{name}_count{wrap} {_num(parts.get('count', 0))}")
    return out


def _gauges() -> dict[str, list[str]]:
    from . import jobs  # jobs imports the labs; keep this module light

    out: dict[str, list[str]] = {"labbox_up": ["labbox_up 1"]}
    try:
        out["labbox_machines_running"] = [f"labbox_machines_running {len(containers.running_workspace_containers())}"]
    except Exception:
        pass
    now = utcnow()
    with Session(engine) as s:
        out["labbox_learners_total"] = [f"labbox_learners_total {s.exec(select(func.count()).select_from(User)).one()}"]
        lines = []
        for window, delta in (("15m", timedelta(minutes=15)), ("24h", timedelta(hours=24))):
            n = s.exec(select(func.count(func.distinct(Workspace.user_id))).where(Workspace.last_active_at >= now - delta)).one()
            lines.append(f'labbox_learners_active{{window="{window}"}} {n}')
        out["labbox_learners_active"] = lines
    runs = jobs.last_runs()
    if runs:
        from datetime import datetime

        out["labbox_job_last_run_timestamp_seconds"] = [
            f'labbox_job_last_run_timestamp_seconds{{job="{j}"}} {int(datetime.fromisoformat(r["at"]).timestamp())}' for j, r in sorted(runs.items())
        ]
        out["labbox_job_last_ok"] = [f'labbox_job_last_ok{{job="{j}"}} {1 if r["ok"] else 0}' for j, r in sorted(runs.items())]
    return out


def render() -> str:
    gauges = _gauges()
    lines: list[str] = []
    for name, (kind, text) in HELP.items():
        if kind == "histogram":
            body = _histogram_lines(name, CHECK_BUCKETS if name.startswith("labbox_check") else DURATION_BUCKETS)
        elif kind == "counter":
            body = _counter_lines(name)
        else:
            body = gauges.get(name, [])
        if body:
            lines += [f"# HELP {name} {text}", f"# TYPE {name} {kind}", *body]
    return "\n".join(lines) + "\n"


def allowed(client_host: str | None, auth_header: str | None) -> bool:
    token = get_settings().METRICS_TOKEN
    if token and auth_header == f"Bearer {token}":
        return True
    return client_host in ("127.0.0.1", "::1", "localhost")

