"""Starts the real local server (langgraph dev) on this chapter's folder, with the fake model behind it."""
import socket
import subprocess
import time
import urllib.request

import pytest
import r
from fake_openai import Reply

STATE = {}


def free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


@pytest.fixture(scope="module")
def server():
    port = free_port()
    log = open("server.log", "w")
    proc = subprocess.Popen(["langgraph", "dev", "--no-browser", "--port", str(port)], stdout=log, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    up = False
    for _ in range(120):
        try:
            urllib.request.urlopen(url + "/ok", timeout=1)
            up = True
            break
        except Exception:  # noqa: BLE001
            if proc.poll() is not None or "failed to load" in open("server.log").read():
                break
            time.sleep(0.5)
    yield url if up else None
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


def load_error() -> str:
    text = open("server.log").read()
    for line in text.splitlines():
        if "failed to load" in line or "Error" in line:
            return line.split("failed to load:")[-1].strip()[:200]
    return "the server did not start"



def test_route_intent():
    def check():
        from harsh.graph import route_intent
        got = [route_intent({"intent": {"kind": k}}) for k in ["status", "rules", "repair", "other", "hello"]]
        if got != ["status", "rules", "repair", "other", "other"]:
            return r.failed("route_intent", "status, rules and repair go to their own nodes; anything else to other.",
                            ["status", "rules", "repair", "other", "other"], got)
        r.passed("route_intent", "Every intent has a place to go, and unknown ones go to a person.")
    r.task("route_intent", check)


def test_approve_over_api(fake, server):
    def check():
        import json
        if not server:
            return r.failed("approve_over_api", "langgraph dev could not load the app: " + load_error())
        from langgraph_sdk import get_sync_client
        from client import decide, say

        def script(body):
            if body.get("response_format"):
                return Reply(json.dumps({"kind": "repair", "problem": "main_burst", "street": "Station Road"}))
            return Reply("ok")
        fake.script = script
        client = get_sync_client(url=server)
        yes, no = client.threads.create()["thread_id"], client.threads.create()["thread_id"]
        paused = say(client, yes, "The main on Station Road has burst!")
        say(client, no, "The main on Station Road has burst!")
        if not paused.get("__interrupt__"):
            return r.failed("approve_over_api", "A Rs 65,000 repair should pause for the engineer (finish route_intent first).")
        approved, refused = decide(client, yes, True, "go"), decide(client, no, False, "no budget")
        last = lambda s: (s or {}).get("messages", [{}])[-1].get("content", "")
        if "A crew is booked for the main burst at Station Road" not in last(approved) or "could not approve" not in last(refused):
            return r.failed("approve_over_api", "Resume with client.runs.wait(thread_id, \"harsh\", command={\"resume\": "
                            "{\"approve\": approve, \"note\": note}}).", "booked / could not approve", (last(approved), last(refused)))
        r.passed("approve_over_api", "The engineer's answer travelled over HTTP and resumed the right paused run.")
    r.task("approve_over_api", check)
