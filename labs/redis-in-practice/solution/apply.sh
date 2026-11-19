#!/usr/bin/env bash
# Used only by `labbox test-lab`: every redis-cli task the way the chapters teach, then the app.
set -euo pipefail
R=(redis-cli)
# Chapter 10 first: every setup has run, so Redis is full and refuses writes until this is fixed.
"${R[@]}" UNLINK debug:log > /dev/null
"${R[@]}" CONFIG SET maxmemory-policy volatile-lru > /dev/null
# Chapter 13's culprit (also big), removed without blocking.
"${R[@]}" UNLINK analytics:raw > /dev/null
# Chapter 1
"${R[@]}" SET shop:name "Brew Point" > /dev/null
"${R[@]}" SET shop:city Pune > /dev/null
"${R[@]}" DEL cups:sold > /dev/null
for _ in 1 2 3; do "${R[@]}" INCR cups:sold > /dev/null; done
"${R[@]}" DECRBY beans:grams 250 > /dev/null
"${R[@]}" --scan --pattern 'tmp:import:*' | xargs -r "${R[@]}" DEL > /dev/null
# Chapter 2
"${R[@]}" SET otp:9876543210 4821 EX 300 > /dev/null
"${R[@]}" EXPIRE session:7f3a 1800 > /dev/null
"${R[@]}" PERSIST promo:diwali > /dev/null
# Chapter 3
"${R[@]}" DEL menu customer:42 orders:pending > /dev/null
"${R[@]}" HSET menu "filter coffee" 30 "cold coffee" 40 "vada pav" 25 > /dev/null
"${R[@]}" HSET customer:42 name Asha visits 7 > /dev/null
"${R[@]}" HINCRBY customer:42 visits 1 > /dev/null
"${R[@]}" HSET customer:42 tier gold > /dev/null
"${R[@]}" LPUSH orders:pending o1 o2 o3 > /dev/null
"${R[@]}" RPOP orders:pending > /dev/null
# Chapter 4
"${R[@]}" DEL visitors:today sales:today > /dev/null
"${R[@]}" SADD visitors:today asha ravi asha meera ravi > /dev/null
"${R[@]}" SINTERSTORE customers:both customers:andheri customers:bandra > /dev/null
"${R[@]}" ZADD sales:today 120 "filter coffee" 80 "vada pav" 45 "cold coffee" > /dev/null
"${R[@]}" ZINCRBY sales:today 5 "cold coffee" > /dev/null
# Chapter 9
"${R[@]}" DEL orders:stream > /dev/null
"${R[@]}" XADD orders:stream '*' order o1 item "filter coffee" > /dev/null
"${R[@]}" XADD orders:stream '*' order o2 item "vada pav" > /dev/null
"${R[@]}" XADD orders:stream '*' order o3 item "cold coffee" > /dev/null
"${R[@]}" XGROUP CREATE orders:stream kitchen 0 > /dev/null
"${R[@]}" XREADGROUP GROUP kitchen barista1 COUNT 3 STREAMS orders:stream '>' > /dev/null
first=$("${R[@]}" XRANGE orders:stream - + COUNT 1 | head -1)
"${R[@]}" XACK orders:stream kitchen "$first" > /dev/null
"${R[@]}" XAUTOCLAIM payments:stream billing worker-2 60000 0 > /dev/null
for id in $("${R[@]}" XRANGE payments:stream - + | grep -E '^[0-9]+-[0-9]+$'); do
  "${R[@]}" XACK payments:stream billing "$id" > /dev/null
done
# Chapter 11
"${R[@]}" CONFIG SET appendonly yes > /dev/null
"${R[@]}" CONFIG SET appendfsync everysec > /dev/null
before=$("${R[@]}" INFO persistence | grep rdb_last_save_time | cut -d: -f2 | tr -d '\r')
"${R[@]}" BGSAVE SCHEDULE > /dev/null
for _ in $(seq 1 100); do
  now=$("${R[@]}" INFO persistence | grep rdb_last_save_time | cut -d: -f2 | tr -d '\r')
  [ "$now" != "$before" ] && break
  sleep 0.2
done
# Chapter 12
redis-cli -h replica REPLICAOF redis 6379 > /dev/null
for _ in $(seq 1 100); do
  redis-cli -h replica INFO replication | grep -q "master_link_status:up" && break
  sleep 0.2
done
"${R[@]}" HSET "{customer:42}:cart" "filter coffee" 2 > /dev/null
"${R[@]}" SADD "{customer:42}:wishlist" poha > /dev/null
# Chapter 5 to 8 and 13: the app in the background
cd /workspace
setsid nohup uvicorn app:app --host 0.0.0.0 --port 8000 > /tmp/app.log 2>&1 < /dev/null &
for _ in $(seq 1 50); do
  curl -s -o /dev/null localhost:8000/docs && exit 0
  sleep 0.2
done
cat /tmp/app.log
exit 1
