"""A stand-in for Deccan Shield's 14-year-old policy system: XML over HTTP on port 8081, and too busy (503) on every third
request, like the real one at month end. You do not change this file. Start it in a second terminal:

    python policy_service.py
"""
import csv
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from xml.sax.saxutils import escape

FIELDS = ["policy_no", "holder", "vehicle_reg", "vehicle", "start_date", "end_date", "sum_insured", "deductible"]
TAGS = {"policy_no": "number", "start_date": "start", "end_date": "end"}


def load(path="data/policies.csv"):
    with open(path, newline="") as f:
        return {row["policy_no"]: row for row in csv.DictReader(f)}


def as_xml(p):
    inner = "".join(f"  <{TAGS.get(k, k)}>{escape(p[k])}</{TAGS.get(k, k)}>\n" for k in FIELDS)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<policy>\n{inner}</policy>\n'


def make_server(port=8081, busy_every=3, path="data/policies.csv"):
    policies = load(path)
    calls = {"n": 0}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            calls["n"] += 1
            if busy_every and calls["n"] % busy_every == 0:
                return self.reply(503, "<error>System busy, try again</error>")
            if not self.path.startswith("/policy/"):
                return self.reply(404, "<error>Unknown path</error>")
            p = policies.get(self.path.rsplit("/", 1)[-1])
            if p is None:
                return self.reply(404, "<error>No such policy</error>")
            self.reply(200, as_xml(p))

        def reply(self, code, body):
            data = body.encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
    print(f"policy system on http://127.0.0.1:{port} (busy on every 3rd request)")
    make_server(port).serve_forever()
