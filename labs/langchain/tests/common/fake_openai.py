"""A fake OpenAI-compatible server for the checks: it records every request and answers from a script.
No network, no model, no cost, the same answer every time."""
import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Toy embeddings: one number per keyword, so texts about the same thing get similar vectors.
WORDS = ["onion", "grape", "tomato", "storage", "loan", "spray", "office", "aadhaar"]


@dataclass
class Reply:
    """What the fake model says: text, or one or more tool calls [(name, args_dict), ...]."""
    text: str | None = None
    tools: list = field(default_factory=list)
    usage: tuple = (42, 8)

    @staticmethod
    def tool(name, args, *more):
        return Reply(tools=[(name, args)] + list(more))


class FakeOpenAI:
    def __init__(self):
        self.chat_requests: list[dict] = []
        self.embedding_requests: list[dict] = []
        self.headers: list[dict] = []
        self.script = lambda body: Reply("Hello from the fake model.")
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                fake.headers.append({k.lower(): v for k, v in self.headers.items()})
                if self.path.endswith("/embeddings"):
                    fake.embedding_requests.append(body)
                    return self.send(200, fake.embeddings(body))
                if not self.path.endswith("/chat/completions"):
                    return self.send(404, {"error": {"message": f"no such path {self.path}"}})
                fake.chat_requests.append(body)
                reply = fake.script(body)
                if isinstance(reply, str):
                    reply = Reply(reply)
                if body.get("stream"):
                    return self.stream(reply)
                self.send(200, fake.completion(reply))

            def send(self, code, obj):
                data = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def stream(self, reply):
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.end_headers()

                def event(delta, finish=None, usage=None):
                    chunk = {"id": "c1", "object": "chat.completion.chunk", "created": 1, "model": "ai-chat",
                             "choices": [] if usage else [{"index": 0, "delta": delta, "finish_reason": finish}]}
                    if usage:
                        chunk["usage"] = usage
                    self.wfile.write(f"data: {json.dumps(chunk)}\n\n".encode())
                    self.wfile.flush()

                event({"role": "assistant", "content": ""})
                if reply.tools:
                    for i, (name, args) in enumerate(reply.tools):
                        event({"tool_calls": [{"index": i, "id": f"call_{i + 1}", "type": "function",
                                               "function": {"name": name, "arguments": json.dumps(args)}}]})
                else:
                    for piece in _pieces(reply.text or ""):
                        event({"content": piece})
                event({}, "tool_calls" if reply.tools else "stop")
                event({}, usage=_usage(reply))
                self.wfile.write(b"data: [DONE]\n\n")

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1"

    def reset(self):
        self.chat_requests.clear()
        self.embedding_requests.clear()
        self.headers.clear()
        self.script = lambda body: Reply("Hello from the fake model.")

    def stop(self):
        self.server.shutdown()

    def completion(self, reply: Reply) -> dict:
        message = {"role": "assistant", "content": reply.text}
        if reply.tools:
            message = {"role": "assistant", "content": None, "tool_calls": [
                {"id": f"call_{i + 1}", "type": "function", "function": {"name": n, "arguments": json.dumps(a)}}
                for i, (n, a) in enumerate(reply.tools)]}
        return {"id": "c1", "object": "chat.completion", "created": 1, "model": "ai-chat",
                "choices": [{"index": 0, "message": message, "finish_reason": "tool_calls" if reply.tools else "stop"}],
                "usage": _usage(reply)}

    def embeddings(self, body: dict) -> dict:
        inputs = body.get("input")
        inputs = [inputs] if isinstance(inputs, str) else inputs
        data = []
        for i, text in enumerate(inputs):
            if not isinstance(text, str):  # token ids: the fake cannot read them
                text = ""
            t = text.lower()
            v = [1.0 if w in t else 0.01 for w in WORDS]
            norm = sum(x * x for x in v) ** 0.5
            data.append({"object": "embedding", "index": i, "embedding": [x / norm for x in v]})
        return {"object": "list", "data": data, "model": "ai-embed", "usage": {"prompt_tokens": 3, "total_tokens": 3}}

    # helpers for checks
    @staticmethod
    def texts(request: dict, role: str) -> list[str]:
        out = []
        for m in request.get("messages", []):
            if m.get("role") == role:
                c = m.get("content")
                if isinstance(c, list):
                    c = " ".join(p.get("text", "") for p in c if isinstance(p, dict))
                out.append(c or "")
        return out

    @staticmethod
    def tool_names(request: dict) -> list[str]:
        return [t["function"]["name"] for t in request.get("tools", [])]


def _usage(reply: Reply) -> dict:
    i, o = reply.usage
    return {"prompt_tokens": i, "completion_tokens": o, "total_tokens": i + o}


def _pieces(text: str) -> list[str]:
    out, word = [], ""
    for ch in text:
        word += ch
        if ch == " ":
            out.append(word)
            word = ""
    if word:
        out.append(word)
    return out
