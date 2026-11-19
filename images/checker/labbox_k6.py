"""Load tests for live checks (system design labs). Runs a k6 script and returns its numbers.

    import labbox_k6
    m = labbox_k6.run(SCRIPT_JS, env={"TARGET": "http://lb:8080"})
    m["p95_ms"], m["error_rate"], m["rps"], m["counts"]["status_429"]
    labbox_k6.report_metric("p95_ms", m["p95_ms"], target=50, better="lower")

Custom counters in the script (`new Counter("status_429")`) come back in m["counts"].
"""
import json
import subprocess
import tempfile
from pathlib import Path


class LoadTestError(Exception):
    pass


def run(script: str, env: dict[str, str] | None = None, timeout: int = 120) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        js, summary = Path(tmp) / "load.js", Path(tmp) / "summary.json"
        js.write_text(script, encoding="utf-8")
        args = ["k6", "run", "--quiet", "--no-color", "--summary-export", str(summary),
                "--summary-trend-stats", "avg,med,p(95),p(99),max", str(js)]
        for k, v in (env or {}).items():
            args += ["-e", f"{k}={v}"]
        try:
            p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise LoadTestError(f"the load test did not finish in {timeout} seconds")
        if not summary.exists():
            out = (p.stderr or p.stdout).strip()
            raise LoadTestError("the load test could not run: " + (out.splitlines()[-1] if out else "no output"))
        data = json.loads(summary.read_text())["metrics"]
    dur = data.get("http_req_duration", {})
    reqs = data.get("http_reqs", {})
    counts = {name: int(m.get("count", 0)) for name, m in data.items() if "count" in m and not name.startswith(("http_", "data_", "iteration", "vus"))}
    return {
        "p50_ms": round(dur.get("med", 0.0), 2),
        "p95_ms": round(dur.get("p(95)", 0.0), 2),
        "p99_ms": round(dur.get("p(99)", 0.0), 2),
        "max_ms": round(dur.get("max", 0.0), 2),
        "requests": int(reqs.get("count", 0)),
        "rps": round(reqs.get("rate", 0.0), 1),
        "error_rate": round(data.get("http_req_failed", {}).get("value", 0.0), 4),
        "counts": counts,
    }


def report_metric(name: str, value: float, target: float | None = None, better: str = "lower") -> None:
    """One @@METRIC line: the lab page shows it as a gauge against the target."""
    m = {"name": name, "value": value, "better": better}
    if target is not None:
        m["target"] = target
    print("@@METRIC " + json.dumps(m), flush=True)
