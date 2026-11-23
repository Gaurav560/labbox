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


def test_server_graph(fake, server):
    def check():
        from harsh.graph import graph
        if graph.checkpointer is not None:
            return r.failed("server_graph", "The server refuses a graph with its own checkpointer: compile with graph.compile().",
                            "no checkpointer", type(graph.checkpointer).__name__)
        if not server:
            return r.failed("server_graph", "langgraph dev could not load the graph: " + load_error())
        from langgraph_sdk import get_sync_client
        fake.script = lambda b: Reply("Please tell me your phone number.")
        client = get_sync_client(url=server)
        thread = client.threads.create()
        state = client.runs.wait(thread["thread_id"], "harsh", input={"messages": [{"role": "user", "content": "Any update?"}]})
        if state["messages"][-1]["content"] != "Please tell me your phone number.":
            return r.failed("server_graph", "The server ran, but the graph did not answer as expected.")
        STATE["ok"] = True
        r.passed("server_graph", "langgraph dev loaded harsh/graph.py and ran it, saving the thread itself.")
    r.task("server_graph", check)


def test_sdk_client(fake, server):
    def check():
        if not server:
            return r.failed("sdk_client", "The server did not start; finish server_graph first.")
        from langgraph_sdk import get_sync_client
        from client import ask
        fake.script = lambda b: Reply(f"seen {len(fake.texts(b, 'user'))}")
        client = get_sync_client(url=server)
        thread = client.threads.create()["thread_id"]
        first, second = ask(client, thread, "Any update?"), ask(client, thread, "98220")
        if (first, second) != ("seen 1", "seen 2"):
            return r.failed("sdk_client", "ask should send the message with client.runs.wait(thread_id, \"harsh\", input={...}) "
                            "and return the last message's content.", ("seen 1", "seen 2"), (first, second))
        r.passed("sdk_client", "Two messages on one server thread: the second run saw the first, kept by the server.")
    r.task("sdk_client", check)
