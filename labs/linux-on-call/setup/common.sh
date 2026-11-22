# Shared by the chapter setups. They run as the learner, once per chapter (again after a reset), and build only
# the practice files of their own chapter folder. Every file is the same for every learner.
set -euo pipefail
export HOME=/home/learner
# fresh FOLDER: go to a chapter folder, creating it if needed.
fresh() { mkdir -p "/workspace/$1"; cd "/workspace/$1"; }
# The Tara status app (chapters 13 and 15): a tiny HTTP server with /health and /tonight.
write_server() {
  cat > server.py <<'PY'
"""The Tara observatory app: GET /health answers ok, GET /tonight answers tonight's plan as JSON (from tonight.json)."""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", "8080"))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tonight.json")) as f:
    TONIGHT = json.load(f)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body, kind = b"ok\n", "text/plain"
        elif self.path == "/tonight":
            body, kind = (json.dumps(TONIGHT, indent=2) + "\n").encode(), "application/json"
        else:
            self.send_error(404, "No such page")
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
print(f"Tara observatory app listening on port {PORT}", flush=True)
server.serve_forever()
PY
  cat > tonight.json <<'JS'
{
  "date": "2026-11-23",
  "site": "Tara Observatory",
  "targets": [
    {"name": "Crab Nebula", "start": "21:00", "dish": 1},
    {"name": "Orion Nebula", "start": "23:30", "dish": 2},
    {"name": "Jupiter", "start": "02:15", "dish": 3}
  ]
}
JS
}
