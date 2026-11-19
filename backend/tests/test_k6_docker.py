"""k6 in the checker image (Phase G): the labbox_k6 helper runs a load test against a tiny HTTP server
in the same container and returns latency, throughput, error rate and custom counters."""
import json
import subprocess

import pytest

pytestmark = pytest.mark.docker

SCRIPT = r"""
import labbox_k6, json, subprocess, time
srv = subprocess.Popen(["python", "-m", "http.server", "8099", "--bind", "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
m = labbox_k6.run('''
import http from "k6/http";
import { Counter } from "k6/metrics";
const ok = new Counter("status_200");
export const options = { vus: 2, iterations: 40 };
export default function () { if (http.get(__ENV.TARGET).status === 200) ok.add(1); }
''', env={"TARGET": "http://127.0.0.1:8099/"})
srv.kill()
labbox_k6.report_metric("p95_ms", m["p95_ms"], target=500)
print(json.dumps(m))
"""


def test_k6_helper_in_the_checker_image():
    try:
        p = subprocess.run(["docker", "run", "--rm", "--user", "1000:1000", "--cap-drop", "ALL", "labbox/checker:v1", "python", "-c", SCRIPT],
                           capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        pytest.skip("Docker is not available")
    if "Unable to find image" in p.stderr:
        pytest.skip("labbox/checker:v1 is not built")
    lines = p.stdout.strip().splitlines()
    assert lines[0].startswith("@@METRIC ") and json.loads(lines[0][9:])["target"] == 500, p.stdout + p.stderr
    m = json.loads(lines[-1])
    assert m["requests"] == 40 and m["counts"]["status_200"] == 40 and m["error_rate"] == 0
    assert 0 < m["p50_ms"] <= m["p95_ms"] <= m["p99_ms"] and m["rps"] > 0
