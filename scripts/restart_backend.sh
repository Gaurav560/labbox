#!/usr/bin/env bash
# Restart the dev backend (4 workers) so it loads new lab content. Keeps SIGNUPS_PER_IP_HOUR from the running one.
# A single stop signal waits for open terminals and websockets, sometimes for minutes; a second one forces it.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${1:-/tmp/labbox-backend.log}"
# the uvicorn main process: its command line is "<venv>/python3.12 <venv>/uvicorn app.main:app ..."
main_pid() { ps -eo pid=,args= | awk '$2 ~ /python/ && $3 ~ /uvicorn$/ && $4 == "app.main:app" {print $1; exit}'; }
M=$(main_pid)
V=""
if [ -n "${M:-}" ]; then
  V=$(tr '\0' '\n' < "/proc/$M/environ" | grep "^SIGNUPS_PER_IP_HOUR=" | cut -d= -f2)
  kill -INT "$M"; sleep 1; kill -INT "$M" 2>/dev/null
  for _ in $(seq 1 60); do ss -ltn | grep -q ':8000 ' || break; sleep 0.5; done
fi
cd "$ROOT/backend" && SIGNUPS_PER_IP_HOUR="${V:-60}" nohup .venv/bin/uvicorn app.main:app --port 8000 --workers 4 > "$LOG" 2>&1 &
for _ in $(seq 1 60); do curl -s -o /dev/null localhost:8000/api/catalog && break; sleep 0.5; done
NEW=$(main_pid)
echo "backend pid $NEW, started $(ps -o lstart= -p "$NEW")"
