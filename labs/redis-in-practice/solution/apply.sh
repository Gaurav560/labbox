#!/usr/bin/env bash
# Used only by `labbox test-lab`: the redis-cli part of chapter 1, then the app in the background.
set -euo pipefail
R=(redis-cli)
"${R[@]}" DEL menu sales:today > /dev/null
"${R[@]}" HSET menu "filter coffee" 30 "cold coffee" 40 "vada pav" 25 > /dev/null
"${R[@]}" SET otp:9876543210 4821 EX 300 > /dev/null
"${R[@]}" ZADD sales:today 120 "filter coffee" 80 "vada pav" 45 "cold coffee" > /dev/null
"${R[@]}" ZINCRBY sales:today 5 "cold coffee" > /dev/null
cd /workspace
setsid nohup uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 < /dev/null &
for _ in $(seq 1 50); do
  curl -s -o /dev/null localhost:8000/docs && exit 0
  sleep 0.2
done
cat /tmp/app.log
exit 1
