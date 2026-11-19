"""Live checks for rate-limiter: real load through the nginx load balancer (k6), counting what got
through. Each run uses fresh API keys, so earlier traffic never counts."""
import json
import time
import uuid

import labbox_k6
import requests

LB = "http://lb:8080"
SECONDS = 3
NOT_RUNNING = "Nothing answers behind the load balancer. Start both copies in the terminal: bash run.sh"

PER_KEY = """
import http from "k6/http";
import { Counter } from "k6/metrics";
http.setResponseCallback(http.expectedStatuses(200, 429));
const okAlice = new Counter("ok_alice"), okBob = new Counter("ok_bob"), sentBob = new Counter("sent_bob"), other = new Counter("other");
export const options = { scenarios: {
  alice: { executor: "constant-arrival-rate", rate: 30, timeUnit: "1s", duration: "%ss", preAllocatedVUs: 15, exec: "alice" },
  bob: { executor: "constant-arrival-rate", rate: 4, timeUnit: "1s", duration: "%ss", preAllocatedVUs: 3, exec: "bob" },
} };
function hit(key) { return http.get(`${__ENV.TARGET}/quote`, { headers: { "X-API-Key": key } }).status; }
export function alice() { const s = hit(__ENV.ALICE); if (s === 200) okAlice.add(1); else if (s !== 429) other.add(1); }
export function bob() { sentBob.add(1); const s = hit(__ENV.BOB); if (s === 200) okBob.add(1); else if (s !== 429) other.add(1); }
""".replace("%s", str(SECONDS))

GLOBAL = """
import http from "k6/http";
import exec from "k6/execution";
import { Counter } from "k6/metrics";
http.setResponseCallback(http.expectedStatuses(200, 429));
const ok = new Counter("ok_total"), other = new Counter("other");
export const options = { scenarios: {
  partners: { executor: "constant-arrival-rate", rate: 80, timeUnit: "1s", duration: "%ss", preAllocatedVUs: 30 },
} };
export default function () {
  const key = `${__ENV.PREFIX}-${exec.scenario.iterationInTest %% 10}`;
  const s = http.get(`${__ENV.TARGET}/quote`, { headers: { "X-API-Key": key } }).status;
  if (s === 200) ok.add(1); else if (s !== 429) other.add(1);
}
""".replace("%%", "%").replace("%s", str(SECONDS))


def report(task, passed, message, expected=None, actual=None):
    r = {"task": task, "passed": passed, "message": message}
    if expected is not None:
        r["expected"], r["actual"] = expected, actual
    print("@@RESULT " + json.dumps(r), flush=True)


def app_up() -> bool:
    for _ in range(10):
        try:
            if requests.get(f"{LB}/health", timeout=2).status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.3)
    return False


def per_key_limit():
    run = uuid.uuid4().hex[:8]
    m = labbox_k6.run(PER_KEY, env={"TARGET": LB, "ALICE": f"alice-{run}", "BOB": f"bob-{run}"})
    c = m["counts"]
    alice = c.get("ok_alice", 0) / SECONDS
    labbox_k6.report_metric("alice_per_second", round(alice, 1), target=10, better="lower")
    labbox_k6.report_metric("p95_ms", m["p95_ms"], target=50, better="lower")
    if c.get("other", 0):
        return report("per_key_limit", False, f"{c['other']} request(s) failed with something other than 200 or 429. Look at /tmp/app-8001.log.")
    if alice > 14:
        return report("per_key_limit", False, f"alice sent 30 a second and got {alice:.0f} a second through. Each server counts on its own.",
                      "about 10 a second", f"{alice:.0f} a second")
    if alice < 8:
        return report("per_key_limit", False, f"alice only got {alice:.1f} a second through; the limit is 10.", "about 10 a second", f"{alice:.1f} a second")
    if c.get("ok_bob", 0) < c.get("sent_bob", 0):
        return report("per_key_limit", False, "bob stayed under his limit but was blocked: each key needs its own count.",
                      f"{c.get('sent_bob', 0)} through", f"{c.get('ok_bob', 0)} through")
    if m["p95_ms"] > 50:
        return report("per_key_limit", False, f"The limit works, but p95 latency is {m['p95_ms']:.0f} ms.", "under 50 ms", f"{m['p95_ms']:.0f} ms")
    report("per_key_limit", True, f"alice: {alice:.1f} a second through, bob untouched, p95 {m['p95_ms']:.0f} ms, on both servers.")


def global_limit():
    time.sleep(1.2)  # a fresh second for the shared counter
    m = labbox_k6.run(GLOBAL, env={"TARGET": LB, "PREFIX": f"p-{uuid.uuid4().hex[:8]}"})
    total = m["counts"].get("ok_total", 0) / SECONDS
    labbox_k6.report_metric("total_per_second", round(total, 1), target=50, better="lower")
    if m["counts"].get("other", 0):
        return report("global_limit", False, f"{m['counts']['other']} request(s) failed with something other than 200 or 429.")
    if total > 60:
        return report("global_limit", False, f"10 partners together sent 80 a second and {total:.0f} a second got through.",
                      "about 50 a second", f"{total:.0f} a second")
    if total < 40:
        return report("global_limit", False, f"Only {total:.0f} a second got through; the global limit is 50.", "about 50 a second", f"{total:.0f} a second")
    report("global_limit", True, f"80 a second came in, {total:.0f} a second got through. The database is safe.")


if not app_up():
    report("per_key_limit", False, NOT_RUNNING)
    report("global_limit", False, NOT_RUNNING)
    raise SystemExit(0)
for check in (per_key_limit, global_limit):
    try:
        check()
    except labbox_k6.LoadTestError as e:
        report(check.__name__, False, f"The load test could not run: {e}")
