"""The /preview and /ide websocket proxy counts real traffic (typing in VS Code) as activity for the
idle reaper, but not tiny keep-alives that an abandoned tab keeps sending. No Docker: fake upstream."""
import asyncio

from fastapi.testclient import TestClient

from app import preview
from app.main import app


class FakeUpstream:
    def __init__(self):
        self.sent = []

    async def send(self, data):
        self.sent.append(data)

    def __aiter__(self):
        return self

    async def __anext__(self):
        await asyncio.sleep(3600)  # the "server" never says anything

    async def close(self):
        pass


def test_only_real_traffic_counts_as_activity(monkeypatch):
    upstream = FakeUpstream()
    touched = []
    monkeypatch.setattr(preview, "_authorize", lambda cookie, lab_id, port, any_port=False: ("user", "lab", "10.0.0.2:3333"))

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(preview.websockets, "connect", connect)
    monkeypatch.setattr(preview, "_touch", lambda user, lab: touched.append((user, lab)))
    with TestClient(app) as client, client.websocket_connect("/preview/python-basics/8000/socket") as ws:
        ws.send_text("ping")  # a keep-alive
        ws.send_text("x" * 200)  # real traffic (typing, saving a file)
        ws.send_text("y" * 200)  # within the same minute: no second database write
        for _ in range(50):
            if len(upstream.sent) == 3:
                break
            asyncio.run(asyncio.sleep(0.02))
    assert upstream.sent[0] == "ping" and len(upstream.sent) == 3  # everything is still forwarded
    assert touched == [("user", "lab")]
