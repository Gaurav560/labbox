#!/usr/bin/env bash
# Used only by `labbox test-lab`: every redis-cli task the way the chapters teach it, then every chapter's
# app at once (one combined app on port 8000, so all app chapters can be checked in one go).
set -euo pipefail
R=(redis-cli)
# Chapter 14 first: every setup has run, so Redis is full and refuses writes until this is fixed.
"${R[@]}" UNLINK debug:log > /dev/null
"${R[@]}" CONFIG SET maxmemory-policy volatile-lru > /dev/null
# Chapter 17's culprit (also big), removed without blocking.
"${R[@]}" UNLINK analytics:raw > /dev/null
# Chapter 1: the numbers redis-cli --latency and redis-benchmark print.
"${R[@]}" SET bench:latency_ms 0.21 > /dev/null
"${R[@]}" SET bench:get_per_sec 88000 > /dev/null
"${R[@]}" SET bench:set_per_sec 86000 > /dev/null
# Chapter 2
"${R[@]}" SET shop:name Basket > /dev/null
"${R[@]}" SET shop:city Pune > /dev/null
"${R[@]}" DEL orders:today > /dev/null
for _ in 1 2 3; do "${R[@]}" INCR orders:today > /dev/null; done
"${R[@]}" DECRBY stock:eggs 12 > /dev/null
"${R[@]}" --scan --pattern 'tmp:import:*' | xargs -r "${R[@]}" DEL > /dev/null
# Chapter 3
"${R[@]}" SET otp:9876543210 4821 EX 300 > /dev/null
"${R[@]}" EXPIRE session:7f3a 1800 > /dev/null
"${R[@]}" PERSIST promo:diwali > /dev/null
# Chapter 4
"${R[@]}" DEL catalogue customer:42 orders:pending > /dev/null
"${R[@]}" HSET catalogue rice 60 dal 120 mangoes 300 > /dev/null
"${R[@]}" HSET customer:42 name Asha orders 7 > /dev/null
"${R[@]}" HINCRBY customer:42 orders 1 > /dev/null
"${R[@]}" HSET customer:42 tier gold > /dev/null
"${R[@]}" LPUSH orders:pending o1 o2 o3 > /dev/null
"${R[@]}" RPOP orders:pending > /dev/null
# Chapter 5
"${R[@]}" DEL visitors:today sales:today > /dev/null
"${R[@]}" SADD visitors:today asha ravi asha meera ravi > /dev/null
"${R[@]}" SINTERSTORE customers:both customers:kothrud customers:baner > /dev/null
"${R[@]}" ZADD sales:today 120 mangoes 80 rice 45 dal > /dev/null
"${R[@]}" ZINCRBY sales:today 5 dal > /dev/null
# Chapter 12
"${R[@]}" DEL orders:stream > /dev/null
"${R[@]}" XADD orders:stream '*' order o1 item rice > /dev/null
"${R[@]}" XADD orders:stream '*' order o2 item dal > /dev/null
"${R[@]}" XADD orders:stream '*' order o3 item mangoes > /dev/null
"${R[@]}" XGROUP CREATE orders:stream packing 0 > /dev/null
"${R[@]}" XREADGROUP GROUP packing packer1 COUNT 3 STREAMS orders:stream '>' > /dev/null
first=$("${R[@]}" XRANGE orders:stream - + COUNT 1 | head -1)
"${R[@]}" XACK orders:stream packing "$first" > /dev/null
"${R[@]}" XAUTOCLAIM payments:stream billing worker-2 60000 0 > /dev/null
for id in $("${R[@]}" XRANGE payments:stream - + | grep -E '^[0-9]+-[0-9]+$'); do
  "${R[@]}" XACK payments:stream billing "$id" > /dev/null
done
# Chapter 13: what the slow log showed, and the slow log switched back on.
"${R[@]}" SET answer:slow_key report:2025 > /dev/null
"${R[@]}" SET answer:slow_command ZRANGE > /dev/null
"${R[@]}" CONFIG SET slowlog-log-slower-than 10000 > /dev/null
"${R[@]}" CONFIG SET slowlog-max-len 1000 > /dev/null
# Chapter 15
"${R[@]}" CONFIG SET appendonly yes > /dev/null
"${R[@]}" CONFIG SET appendfsync everysec > /dev/null
before=$("${R[@]}" INFO persistence | grep rdb_last_save_time | cut -d: -f2 | tr -d '\r')
"${R[@]}" BGSAVE SCHEDULE > /dev/null
for _ in $(seq 1 100); do
  now=$("${R[@]}" INFO persistence | grep rdb_last_save_time | cut -d: -f2 | tr -d '\r')
  [ "$now" != "$before" ] && break
  sleep 0.2
done
# Chapter 16
redis-cli -h replica REPLICAOF redis 6379 > /dev/null
for _ in $(seq 1 100); do
  redis-cli -h replica INFO replication | grep -q "master_link_status:up" && break
  sleep 0.2
done
"${R[@]}" HSET "{customer:42}:cart" rice 2 > /dev/null
"${R[@]}" SADD "{customer:42}:wishlist" mangoes > /dev/null
# Chapters 6 to 11 and 17: one app made of every chapter's app. Later chapters first, so that
# chapter 9's /price (cache, counters, lock) answers for chapters 7 and 8 too.
cat > /tmp/all_app.py <<'PY'
import importlib.util
import sys

from fastapi import FastAPI

app = FastAPI()
for folder in ["17-capstone", "11-locks", "10-atomic-operations", "09-stampede", "08-cache-savings", "06-redis-from-python"]:
    sys.path.insert(0, f"/workspace/{folder}")
    spec = importlib.util.spec_from_file_location(f"chapter_{folder[:2]}", f"/workspace/{folder}/app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    app.include_router(module.app.router)
PY
cd /workspace/06-redis-from-python  # /import reads data/sales.csv from here
setsid nohup uvicorn all_app:app --app-dir /tmp --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 < /dev/null &
for _ in $(seq 1 50); do
  curl -s -o /dev/null localhost:8000/docs && exit 0
  sleep 0.2
done
cat /tmp/app.log
exit 1
